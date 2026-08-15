import cv2
import time
import os
from datetime import datetime

from backend.api.services.analytics_service import update
from backend.api.services.alert_service import add_alert
from backend.database.database import SessionLocal
from backend.database.crud import save_record
from backend.core.tracker import detect_and_track
from backend.core.heatmap import Heatmap
from backend.core.line_counter import LineCounter
from backend.core.restricted_zone import RestrictedZone
from backend.config.settings import VIDEO_SOURCE


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)

INCIDENT_FOLDER = os.path.join(
    BASE_DIR,
    "assets",
    "incidents"
)

os.makedirs(
    INCIDENT_FOLDER,
    exist_ok=True
)


# ============================================================
# VIDEO SOURCE CONFIGURATION
# ============================================================

# Render environment variable overrides settings.py
VIDEO_SOURCE_ENV = os.getenv(
    "VIDEO_SOURCE",
    VIDEO_SOURCE
)


def get_video_source():
    """
    Convert VIDEO_SOURCE into a usable OpenCV source.

    Supported:

        0
        "0"
        "assets/videos/traffic.mp4"
        "rtsp://..."
        "http://..."
        "https://..."
    """

    source = VIDEO_SOURCE_ENV

    # --------------------------------------------------------
    # Direct integer source
    # --------------------------------------------------------

    if isinstance(source, int):
        return source

    # --------------------------------------------------------
    # String source
    # --------------------------------------------------------

    if isinstance(source, str):

        source = source.strip()

        # Webcam index supplied through environment variable
        if source.isdigit():
            return int(source)

        # Remote source
        if source.startswith(
            (
                "rtsp://",
                "http://",
                "https://"
            )
        ):
            return source

        # Local file
        if not os.path.isabs(source):

            source = os.path.join(
                BASE_DIR,
                source
            )

        return source

    return source


VIDEO_SOURCE_VALUE = get_video_source()


print("========================================")
print("VisionEdge Video Source")
print(f"Source: {VIDEO_SOURCE_VALUE}")
print("========================================")


# ============================================================
# VIDEO CAMERA
# ============================================================

camera = None


def open_camera():
    """
    Open the configured video source.
    """

    global camera

    if camera is not None:

        try:
            camera.release()
        except Exception:
            pass

    print(
        f"[INFO] Opening video source: "
        f"{VIDEO_SOURCE_VALUE}"
    )

    camera = cv2.VideoCapture(
        VIDEO_SOURCE_VALUE
    )

    if not camera.isOpened():

        print(
            "[ERROR] Could not open video source: "
            f"{VIDEO_SOURCE_VALUE}"
        )

        return False

    # --------------------------------------------------------
    # Reduce internal buffering for live sources
    # --------------------------------------------------------

    try:

        camera.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )

    except Exception:
        pass

    print(
        "[INFO] Video source opened successfully: "
        f"{VIDEO_SOURCE_VALUE}"
    )

    return True


# Open video once during startup
open_camera()


# ============================================================
# VISIONEDGE ANALYTICS COMPONENTS
# ============================================================

heatmap = Heatmap()

line_counter = LineCounter()

restricted_zone = RestrictedZone()


# ============================================================
# TIMING
# ============================================================

prev_time = time.time()


# ============================================================
# INTRUSION SETTINGS
# ============================================================

last_intrusion_time = {}

INTRUSION_COOLDOWN = 10


# ============================================================
# ALERT THROTTLING
# ============================================================

last_crowd_alert_time = 0

last_traffic_alert_time = 0

ALERT_COOLDOWN = 10


# ============================================================
# DATABASE THROTTLING
# ============================================================

last_database_save_time = 0

DATABASE_SAVE_INTERVAL = 1.0


# ============================================================
# STREAM SETTINGS
# ============================================================

# Resize very large videos to reduce Render CPU usage.
MAX_FRAME_WIDTH = 1280


# ============================================================
# HELPER: RESIZE FRAME
# ============================================================

def resize_frame(frame):

    height, width = frame.shape[:2]

    if width <= MAX_FRAME_WIDTH:
        return frame

    scale = MAX_FRAME_WIDTH / width

    new_width = int(width * scale)

    new_height = int(height * scale)

    return cv2.resize(
        frame,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_AREA
    )


# ============================================================
# HELPER: CREATE ERROR FRAME
# ============================================================

def create_error_frame(message):

    frame = (
        30
        * __import__("numpy").ones(
            (480, 854, 3),
            dtype="uint8"
        )
    )

    cv2.putText(
        frame,
        "VisionEdge",
        (40, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        (255, 255, 255),
        3
    )

    cv2.putText(
        frame,
        message,
        (40, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

    success, buffer = cv2.imencode(
        ".jpg",
        frame
    )

    if not success:
        return None

    return buffer.tobytes()


# ============================================================
# FRAME GENERATOR
# ============================================================

def generate_frames():

    global camera
    global prev_time
    global last_crowd_alert_time
    global last_traffic_alert_time
    global last_database_save_time

    print("[INFO] VisionEdge video stream started.")

    # --------------------------------------------------------
    # Make sure camera is available
    # --------------------------------------------------------

    if camera is None or not camera.isOpened():

        if not open_camera():

            error_frame = create_error_frame(
                "Video source could not be opened."
            )

            if error_frame:

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: "
                    + str(len(error_frame)).encode()
                    + b"\r\n\r\n"
                    + error_frame
                    + b"\r\n"
                )

            return

    # ========================================================
    # MAIN STREAM LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # READ FRAME
        # ----------------------------------------------------

        success, frame = camera.read()

        # ----------------------------------------------------
        # VIDEO EOF / CAMERA FAILURE
        # ----------------------------------------------------

        if not success:

            print(
                "[INFO] Video frame could not be read."
            )

            # ------------------------------------------------
            # Prerecorded video
            # ------------------------------------------------

            if isinstance(
                VIDEO_SOURCE_VALUE,
                str
            ) and not VIDEO_SOURCE_VALUE.startswith(
                (
                    "rtsp://",
                    "http://",
                    "https://"
                )
            ):

                print(
                    "[INFO] Restarting demo video..."
                )

                try:

                    camera.set(
                        cv2.CAP_PROP_POS_FRAMES,
                        0
                    )

                    success, frame = camera.read()

                except Exception as exc:

                    print(
                        "[ERROR] Could not restart video: "
                        f"{exc}"
                    )

                    success = False

            # ------------------------------------------------
            # Reopen camera if restart failed
            # ------------------------------------------------

            if not success:

                print(
                    "[INFO] Reopening video source..."
                )

                if not open_camera():

                    time.sleep(1)

                    continue

                success, frame = camera.read()

                if not success:

                    time.sleep(1)

                    continue

        # ----------------------------------------------------
        # Resize frame for Render performance
        # ----------------------------------------------------

        frame = resize_frame(frame)

        # ====================================================
        # FPS
        # ====================================================

        current_time = time.time()

        elapsed = (
            current_time - prev_time
        )

        if elapsed > 0:

            fps = 1 / elapsed

        else:

            fps = 0

        prev_time = current_time

        # ====================================================
        # YOLO DETECTION + TRACKING
        # ====================================================

        try:

            # IMPORTANT:
            #
            # detect_and_track() already performs YOLO
            # inference.
            #
            # DO NOT load another YOLO model here.
            #

            results = detect_and_track(
                frame
            )

        except Exception as exc:

            print(
                "[ERROR] Detection failed: "
                f"{exc}"
            )

            error_frame = create_error_frame(
                "AI detection temporarily unavailable."
            )

            if error_frame:

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: "
                    + str(len(error_frame)).encode()
                    + b"\r\n\r\n"
                    + error_frame
                    + b"\r\n"
                )

            time.sleep(0.1)

            continue

        # ----------------------------------------------------
        # Validate YOLO result
        # ----------------------------------------------------

        if (
            results is None
            or len(results) == 0
        ):

            continue

        result = results[0]

        # ====================================================
        # CLASS NAMES
        # ====================================================

        names = result.names

        # ====================================================
        # OBJECT COUNTS
        # ====================================================

        counts = {
            "people": 0,
            "cars": 0,
            "buses": 0,
            "motorcycles": 0,
        }

        # ====================================================
        # HEATMAP
        # ====================================================

        try:

            if (
                result.boxes is not None
                and len(result.boxes) > 0
            ):

                boxes = (
                    result
                    .boxes
                    .xyxy
                    .cpu()
                    .numpy()
                )

                heatmap.update(
                    frame,
                    boxes
                )

        except Exception as exc:

            print(
                "[WARNING] Heatmap update failed: "
                f"{exc}"
            )

        # ====================================================
        # PROCESS DETECTED OBJECTS
        # ====================================================

        if (
            result.boxes is not None
            and len(result.boxes) > 0
        ):

            for box in result.boxes:

                # ------------------------------------------------
                # CLASS
                # ------------------------------------------------

                try:

                    cls = int(
                        box.cls[0]
                    )

                    label = names[cls]

                except Exception:

                    continue

                # ------------------------------------------------
                # OBJECT COUNTING
                # ------------------------------------------------

                if label == "person":

                    counts["people"] += 1

                elif label == "car":

                    counts["cars"] += 1

                elif label == "bus":

                    counts["buses"] += 1

                elif label == "motorcycle":

                    counts["motorcycles"] += 1

                # ------------------------------------------------
                # TRACKING
                # ------------------------------------------------

                if box.id is None:

                    continue

                try:

                    track_id = int(
                        box.id[0]
                    )

                    x1, y1, x2, y2 = (
                        box.xyxy[0]
                    )

                    center_x = int(
                        (x1 + x2) / 2
                    )

                    center_y = int(
                        (y1 + y2) / 2
                    )

                except Exception:

                    continue

                # =================================================
                # LINE COUNTER
                # =================================================

                try:

                    line_counter.update(
                        track_id,
                        label,
                        center_y
                    )

                except Exception as exc:

                    print(
                        "[WARNING] Line counter failed: "
                        f"{exc}"
                    )

                # =================================================
                # RESTRICTED ZONE
                # =================================================

                try:

                    inside_zone = (
                        label == "person"
                        and restricted_zone.contains(
                            center_x,
                            center_y
                        )
                    )

                except Exception:

                    inside_zone = False

                if inside_zone:

                    current_time = time.time()

                    last_time = (
                        last_intrusion_time.get(
                            track_id,
                            0
                        )
                    )

                    # ------------------------------------------------
                    # Intrusion cooldown
                    # ------------------------------------------------

                    if (
                        current_time - last_time
                        >= INTRUSION_COOLDOWN
                    ):

                        timestamp = (
                            datetime.now()
                            .strftime(
                                "%Y%m%d_%H%M%S"
                            )
                        )

                        filename = (
                            f"intrusion_"
                            f"{track_id}_"
                            f"{timestamp}.jpg"
                        )

                        filepath = os.path.join(
                            INCIDENT_FOLDER,
                            filename
                        )

                        # Save screenshot
                        try:

                            cv2.imwrite(
                                filepath,
                                frame
                            )

                            print(
                                "[ALERT] Intrusion screenshot "
                                f"saved: {filepath}"
                            )

                        except Exception as exc:

                            print(
                                "[ERROR] Could not save "
                                f"intrusion screenshot: {exc}"
                            )

                        # Update cooldown
                        last_intrusion_time[
                            track_id
                        ] = current_time

                        # Create alert
                        try:

                            add_alert(
                                f"🚨 Intrusion Detected! "
                                f"Screenshot: {filename}"
                            )

                        except Exception as exc:

                            print(
                                "[WARNING] Could not create "
                                f"intrusion alert: {exc}"
                            )

        # ====================================================
        # ANALYTICS
        # ====================================================

        analytics = {

            "people":
                counts["people"],

            "cars":
                counts["cars"],

            "buses":
                counts["buses"],

            "motorcycles":
                counts["motorcycles"],

            "fps":
                round(
                    fps,
                    2
                ),

            "line_crossings":
                line_counter.people_crossed,
        }

        # ----------------------------------------------------
        # Update in-memory analytics
        # ----------------------------------------------------

        try:

            update(
                analytics
            )

        except Exception as exc:

            print(
                "[WARNING] Analytics update failed: "
                f"{exc}"
            )

        # ====================================================
        # DATABASE
        # ====================================================

        current_time = time.time()

        if (
            current_time - last_database_save_time
            >= DATABASE_SAVE_INTERVAL
        ):

            db = SessionLocal()

            try:

                save_record(
                    db,
                    analytics
                )

                last_database_save_time = (
                    current_time
                )

            except Exception as exc:

                print(
                    "[WARNING] Database save failed: "
                    f"{exc}"
                )

            finally:

                db.close()

        # ====================================================
        # CROWD ALERT
        # ====================================================

        if (
            counts["people"] >= 3
            and
            current_time - last_crowd_alert_time
            >= ALERT_COOLDOWN
        ):

            try:

                add_alert(
                    f"Crowd Alert: "
                    f"{counts['people']} people detected"
                )

                last_crowd_alert_time = (
                    current_time
                )

            except Exception as exc:

                print(
                    "[WARNING] Crowd alert failed: "
                    f"{exc}"
                )

        # ====================================================
        # TRAFFIC ALERT
        # ====================================================

        if (
            counts["cars"] >= 5
            and
            current_time - last_traffic_alert_time
            >= ALERT_COOLDOWN
        ):

            try:

                add_alert(
                    f"Traffic Alert: "
                    f"{counts['cars']} cars detected"
                )

                last_traffic_alert_time = (
                    current_time
                )

            except Exception as exc:

                print(
                    "[WARNING] Traffic alert failed: "
                    f"{exc}"
                )

        # ====================================================
        # DRAW YOLO DETECTIONS
        # ====================================================

        try:

            annotated = result.plot()

        except Exception as exc:

            print(
                "[WARNING] Could not draw detections: "
                f"{exc}"
            )

            annotated = frame.copy()

        # ====================================================
        # DRAW HEATMAP
        # ====================================================

        try:

            annotated = heatmap.draw(
                annotated
            )

        except Exception as exc:

            print(
                "[WARNING] Heatmap drawing failed: "
                f"{exc}"
            )

        # ====================================================
        # DRAW RESTRICTED ZONE
        # ====================================================

        try:

            annotated = restricted_zone.draw(
                annotated
            )

        except Exception as exc:

            print(
                "[WARNING] Restricted zone drawing "
                f"failed: {exc}"
            )

        # ====================================================
        # DRAW COUNTING LINE
        # ====================================================

        try:

            cv2.line(
                annotated,

                (
                    0,
                    line_counter.line_y
                ),

                (
                    annotated.shape[1],
                    line_counter.line_y
                ),

                (0, 255, 255),

                3
            )

        except Exception as exc:

            print(
                "[WARNING] Counting line drawing "
                f"failed: {exc}"
            )

        # ====================================================
        # PEOPLE CROSSED
        # ====================================================

        cv2.putText(
            annotated,

            (
                f"People Crossed: "
                f"{line_counter.people_crossed}"
            ),

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 255, 0),

            2
        )

        # ====================================================
        # CARS CROSSED
        # ====================================================

        cv2.putText(
            annotated,

            (
                f"Cars Crossed: "
                f"{line_counter.cars_crossed}"
            ),

            (20, 75),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 0, 0),

            2
        )

        # ====================================================
        # FPS
        # ====================================================

        cv2.putText(
            annotated,

            f"FPS: {round(fps, 1)}",

            (20, 110),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 255, 255),

            2
        )

        # ====================================================
        # VISIONEDGE STATUS
        # ====================================================

        cv2.putText(
            annotated,

            "VisionEdge AI",

            (
                20,
                annotated.shape[0] - 20
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2
        )

        # ====================================================
        # JPEG ENCODING
        # ====================================================

        success, buffer = cv2.imencode(
            ".jpg",
            annotated,
            [
                int(cv2.IMWRITE_JPEG_QUALITY),
                80
            ]
        )

        if not success:

            print(
                "[WARNING] JPEG encoding failed."
            )

            continue

        frame_bytes = buffer.tobytes()

        # ====================================================
        # MJPEG STREAM
        # ====================================================

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: "
            + str(len(frame_bytes)).encode()
            + b"\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )