import cv2
import time
import os
import threading
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
        "..",
    )
)


INCIDENT_FOLDER = os.path.join(
    BASE_DIR,
    "assets",
    "incidents",
)


os.makedirs(
    INCIDENT_FOLDER,
    exist_ok=True,
)


# ============================================================
# VIDEO SOURCE
# ============================================================

VIDEO_SOURCE_ENV = os.getenv(
    "VIDEO_SOURCE",
    VIDEO_SOURCE,
)


def get_video_source():
    """
    Supported sources:

        0
        "0"
        "assets/videos/traffic.mp4"
        "C:/Videos/traffic.mp4"
        "rtsp://..."
        "http://..."
        "https://..."
    """

    source = VIDEO_SOURCE_ENV

    # --------------------------------------------------------
    # Integer webcam
    # --------------------------------------------------------

    if isinstance(source, int):
        return source

    # --------------------------------------------------------
    # String source
    # --------------------------------------------------------

    if isinstance(source, str):

        source = source.strip()

        # Webcam through environment variable
        if source.isdigit():
            return int(source)

        # Remote stream
        if source.startswith(
            (
                "rtsp://",
                "http://",
                "https://",
            )
        ):
            return source

        # Local video file
        if not os.path.isabs(source):

            source = os.path.join(
                BASE_DIR,
                source,
            )

        return source

    return source


VIDEO_SOURCE_VALUE = get_video_source()


print("========================================")
print("VisionEdge Video Source")
print(f"Source: {VIDEO_SOURCE_VALUE}")
print("========================================")


# ============================================================
# SOURCE TYPE
# ============================================================

IS_WEBCAM = isinstance(
    VIDEO_SOURCE_VALUE,
    int,
)


IS_FILE = (
    isinstance(VIDEO_SOURCE_VALUE, str)
    and os.path.isfile(VIDEO_SOURCE_VALUE)
)


# ============================================================
# VIDEO CAPTURE
# ============================================================

camera_lock = threading.Lock()


camera = cv2.VideoCapture(
    VIDEO_SOURCE_VALUE
)


# ============================================================
# CAMERA SETTINGS
# ============================================================

if IS_WEBCAM:

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280,
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720,
    )

    camera.set(
        cv2.CAP_PROP_FPS,
        30,
    )


# ============================================================
# CAMERA STATUS
# ============================================================

if not camera.isOpened():

    print(
        "[ERROR] Could not open video source: "
        f"{VIDEO_SOURCE_VALUE}"
    )

else:

    print(
        "[INFO] Video source opened successfully: "
        f"{VIDEO_SOURCE_VALUE}"
    )


# ============================================================
# VISIONEDGE COMPONENTS
# ============================================================

heatmap = Heatmap()

line_counter = LineCounter()

restricted_zone = RestrictedZone()


# ============================================================
# FPS
# ============================================================

prev_time = time.time()


# ============================================================
# INTRUSION COOLDOWN
# ============================================================

last_intrusion_time = {}

INTRUSION_COOLDOWN = 10


# ============================================================
# ANALYTICS INITIALIZATION
# ============================================================

update(
    {
        "fps": 0.0,
        "people": 0,
        "cars": 0,
        "buses": 0,
        "motorcycles": 0,
        "line_crossings": 0,
    }
)


# ============================================================
# REOPEN VIDEO SOURCE
# ============================================================

def reopen_camera():

    global camera

    with camera_lock:

        try:

            if camera is not None:

                camera.release()

        except Exception:

            pass


        camera = cv2.VideoCapture(
            VIDEO_SOURCE_VALUE
        )


        if IS_WEBCAM:

            camera.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                1280,
            )

            camera.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                720,
            )

            camera.set(
                cv2.CAP_PROP_FPS,
                30,
            )


        return camera.isOpened()


# ============================================================
# READ FRAME
# ============================================================

def read_frame():

    global camera

    with camera_lock:

        if camera is None:

            return False, None

        success, frame = camera.read()

    return success, frame


# ============================================================
# PROCESS ONE FRAME
# ============================================================

def process_frame(frame):

    global prev_time

    # ========================================================
    # FPS
    # ========================================================

    current_time = time.time()

    elapsed = (
        current_time - prev_time
    )

    if elapsed > 0:

        fps = 1 / elapsed

    else:

        fps = 0.0

    prev_time = current_time


    # ========================================================
    # YOLO DETECTION + TRACKING
    # ========================================================

    try:

        results = detect_and_track(
            frame
        )

    except Exception as e:

        print(
            f"[ERROR] YOLO detection error: {e}"
        )

        return None


    if not results:

        return None


    result = results[0]


    # ========================================================
    # CLASS NAMES
    # ========================================================

    names = result.names


    # ========================================================
    # OBJECT COUNTS
    # ========================================================

    counts = {
        "people": 0,
        "cars": 0,
        "buses": 0,
        "motorcycles": 0,
    }


    # ========================================================
    # HEATMAP
    # ========================================================

    try:

        boxes = (
            result
            .boxes
            .xyxy
            .cpu()
            .numpy()
        )

    except Exception:

        boxes = []


    if len(boxes) > 0:

        try:

            heatmap.update(
                frame,
                boxes,
            )

        except Exception as e:

            print(
                f"[WARNING] Heatmap error: {e}"
            )


    # ========================================================
    # PROCESS DETECTIONS
    # ========================================================

    for box in result.boxes:

        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        try:

            cls = int(
                box.cls[0]
            )

            label = names[cls]

        except Exception:

            continue


        # ----------------------------------------------------
        # OBJECT COUNT
        # ----------------------------------------------------

        if label == "person":

            counts["people"] += 1

        elif label == "car":

            counts["cars"] += 1

        elif label == "bus":

            counts["buses"] += 1

        elif label == "motorcycle":

            counts["motorcycles"] += 1


        # ----------------------------------------------------
        # TRACK ID
        # ----------------------------------------------------

        if box.id is None:

            continue


        try:

            track_id = int(
                box.id[0]
            )

        except Exception:

            continue


        # ----------------------------------------------------
        # BOUNDING BOX CENTER
        # ----------------------------------------------------

        try:

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


        # ====================================================
        # LINE COUNTER
        # ====================================================

        try:

            line_counter.update(
                track_id,
                label,
                center_y,
            )

        except Exception as e:

            print(
                f"[WARNING] Line counter error: {e}"
            )


        # ====================================================
        # RESTRICTED ZONE
        # ====================================================

        if label == "person":

            try:

                inside_zone = (
                    restricted_zone.contains(
                        center_x,
                        center_y,
                    )
                )

            except Exception:

                inside_zone = False


            if inside_zone:

                current_intrusion_time = (
                    time.time()
                )

                last_time = (
                    last_intrusion_time.get(
                        track_id,
                        0,
                    )
                )


                if (
                    current_intrusion_time
                    - last_time
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
                        filename,
                    )


                    try:

                        cv2.imwrite(
                            filepath,
                            frame,
                        )

                    except Exception as e:

                        print(
                            "[WARNING] "
                            f"Could not save intrusion image: {e}"
                        )


                    last_intrusion_time[
                        track_id
                    ] = (
                        current_intrusion_time
                    )


                    try:

                        add_alert(
                            "🚨 Intrusion Detected! "
                            f"Screenshot: {filename}"
                        )

                    except Exception as e:

                        print(
                            f"[WARNING] Alert error: {e}"
                        )


                    print(
                        "[ALERT] Intrusion screenshot "
                        f"saved: {filepath}"
                    )


    # ========================================================
    # LINE CROSSINGS
    # ========================================================

    people_crossed = (
        line_counter.people_crossed
    )

    cars_crossed = (
        line_counter.cars_crossed
    )


    # ========================================================
    # ANALYTICS
    # ========================================================

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
                2,
            ),

        "line_crossings":
            people_crossed,
    }


    # ========================================================
    # UPDATE LIVE ANALYTICS
    # ========================================================

    try:

        update(
            analytics
        )

    except Exception as e:

        print(
            f"[WARNING] Analytics update error: {e}"
        )


    # ========================================================
    # DATABASE
    # ========================================================

    db = SessionLocal()

    try:

        save_record(
            db,
            analytics,
        )

    except Exception as e:

        print(
            f"[WARNING] Database error: {e}"
        )

    finally:

        db.close()


    # ========================================================
    # CROWD ALERT
    # ========================================================

    if counts["people"] >= 3:

        try:

            add_alert(
                "Crowd Alert: "
                f"{counts['people']} people detected"
            )

        except Exception as e:

            print(
                f"[WARNING] Crowd alert error: {e}"
            )


    # ========================================================
    # TRAFFIC ALERT
    # ========================================================

    if counts["cars"] >= 5:

        try:

            add_alert(
                "Traffic Alert: "
                f"{counts['cars']} cars detected"
            )

        except Exception as e:

            print(
                f"[WARNING] Traffic alert error: {e}"
            )


    # ========================================================
    # YOLO ANNOTATION
    # ========================================================

    try:

        annotated = result.plot()

    except Exception:

        annotated = frame.copy()


    # ========================================================
    # HEATMAP
    # ========================================================

    try:

        annotated = heatmap.draw(
            annotated
        )

    except Exception as e:

        print(
            f"[WARNING] Heatmap drawing error: {e}"
        )


    # ========================================================
    # RESTRICTED ZONE
    # ========================================================

    try:

        annotated = restricted_zone.draw(
            annotated
        )

    except Exception as e:

        print(
            "[WARNING] Restricted zone "
            f"drawing error: {e}"
        )


    # ========================================================
    # COUNTING LINE
    # ========================================================

    try:

        cv2.line(
            annotated,

            (
                0,
                line_counter.line_y,
            ),

            (
                annotated.shape[1],
                line_counter.line_y,
            ),

            (0, 255, 255),

            3,
        )

    except Exception as e:

        print(
            f"[WARNING] Line drawing error: {e}"
        )


    # ========================================================
    # PEOPLE CROSSED
    # ========================================================

    cv2.putText(
        annotated,

        (
            f"People Crossed: "
            f"{people_crossed}"
        ),

        (20, 40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0, 255, 0),

        2,
    )


    # ========================================================
    # CARS CROSSED
    # ========================================================

    cv2.putText(
        annotated,

        (
            f"Cars Crossed: "
            f"{cars_crossed}"
        ),

        (20, 75),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (255, 0, 0),

        2,
    )


    # ========================================================
    # FPS
    # ========================================================

    cv2.putText(
        annotated,

        f"FPS: {round(fps, 1)}",

        (20, 110),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (255, 255, 255),

        2,
    )


    # ========================================================
    # SOURCE LABEL
    # ========================================================

    source_label = (
        "LIVE WEBCAM"
        if IS_WEBCAM
        else "DEMO VIDEO"
    )


    cv2.putText(
        annotated,

        source_label,

        (20, 145),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (0, 255, 255),

        2,
    )


    # ========================================================
    # JPEG ENCODING
    # ========================================================

    success, buffer = cv2.imencode(
        ".jpg",
        annotated,
    )


    if not success:

        return None


    return buffer.tobytes()


# ============================================================
# FRAME GENERATOR
# ============================================================

def generate_frames():

    global camera

    print(
        "[INFO] VisionEdge frame generator started."
    )


    while True:

        # ====================================================
        # READ FRAME
        # ====================================================

        success, frame = read_frame()


        # ====================================================
        # VIDEO FILE LOOP
        # ====================================================

        if not success:

            if IS_FILE:

                print(
                    "[INFO] Video reached end. "
                    "Restarting..."
                )


                with camera_lock:

                    camera.set(
                        cv2.CAP_PROP_POS_FRAMES,
                        0,
                    )


                time.sleep(
                    0.05
                )

                continue


            # =================================================
            # WEBCAM / REMOTE FAILURE
            # =================================================

            print(
                "[WARNING] Could not read "
                "frame from video source."
            )


            time.sleep(
                0.1
            )


            # Try reopening
            if not reopen_camera():

                time.sleep(
                    1
                )


            continue


        # ====================================================
        # PROCESS FRAME
        # ====================================================

        frame_bytes = process_frame(
            frame
        )


        if frame_bytes is None:

            continue


        # ====================================================
        # MJPEG STREAM
        # ====================================================

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: "
            + str(
                len(frame_bytes)
            ).encode()
            + b"\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )