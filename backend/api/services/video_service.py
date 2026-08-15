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

    source = VIDEO_SOURCE_ENV

    if isinstance(source, int):

        return source


    if isinstance(source, str):

        source = source.strip()


        if source.isdigit():

            return int(source)


        if source.startswith(
            (
                "rtsp://",
                "http://",
                "https://",
            )
        ):

            return source


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
    isinstance(
        VIDEO_SOURCE_VALUE,
        str,
    )
    and
    os.path.isfile(
        VIDEO_SOURCE_VALUE
    )
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
# LATEST AI RESULT
# ============================================================

latest_result = {
    "people": 0,
    "cars": 0,
    "buses": 0,
    "motorcycles": 0,
    "fps": 0.0,
    "line_crossings": 0,
    "detections": [],
    "intrusion": False,
}


latest_result_lock = threading.Lock()


# ============================================================
# ANALYTICS INITIALIZATION
# ============================================================

try:

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

except Exception as e:

    print(
        "[WARNING] Analytics initialization error:",
        e,
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
# GET LATEST AI RESULT
# ============================================================

def get_latest_result():

    with latest_result_lock:

        return latest_result.copy()


# ============================================================
# SAVE ANALYTICS RECORD
# ============================================================

def save_analytics_record(analytics):

    db = SessionLocal()

    try:

        save_record(
            db,
            analytics,
        )

    except Exception as e:

        print(
            "[WARNING] Database error:",
            e,
        )

    finally:

        db.close()


# ============================================================
# PROCESS SERVER VIDEO FRAME
# ============================================================

def process_frame(frame):

    global prev_time
    global latest_result


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


    names = result.names


    counts = {
        "people": 0,
        "cars": 0,
        "buses": 0,
        "motorcycles": 0,
    }


    detections = []

    intrusion_detected = False


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

        try:

            cls = int(
                box.cls[0]
            )

            label = names[cls]

            confidence = float(
                box.conf[0]
            )

        except Exception:

            continue


        # ----------------------------------------------------
        # COUNTS
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
        # BOUNDING BOX
        # ----------------------------------------------------

        try:

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

        except Exception:

            continue


        # ----------------------------------------------------
        # TRACK ID
        # ----------------------------------------------------

        track_id = None

        if box.id is not None:

            try:

                track_id = int(
                    box.id[0]
                )

            except Exception:

                track_id = None


        center_x = int(
            (x1 + x2) / 2
        )

        center_y = int(
            (y1 + y2) / 2
        )


        # ====================================================
        # INTRUSION
        # ====================================================

        is_intrusion = False


        if label == "person":

            try:

                is_intrusion = (
                    restricted_zone.contains(
                        center_x,
                        center_y,
                    )
                )

            except Exception:

                is_intrusion = False


            if is_intrusion:

                intrusion_detected = True

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
                    track_id is not None
                    and
                    (
                        current_intrusion_time
                        - last_time
                    )
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
                            "Could not save intrusion image:",
                            e,
                        )


                    last_intrusion_time[
                        track_id
                    ] = current_intrusion_time


                    try:

                        add_alert(
                            "🚨 Intrusion Detected! "
                            f"Screenshot: {filename}"
                        )

                    except Exception as e:

                        print(
                            "[WARNING] Alert error:",
                            e,
                        )


                    print(
                        "[ALERT] Intrusion screenshot saved:",
                        filepath,
                    )


        # ====================================================
        # LINE COUNTER
        # ====================================================

        if track_id is not None:

            try:

                line_counter.update(
                    track_id,
                    label,
                    center_y,
                )

            except Exception as e:

                print(
                    "[WARNING] "
                    "Line counter error:",
                    e,
                )


        detections.append(
            {
                "class": label,
                "confidence": round(
                    confidence,
                    3,
                ),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "track_id": track_id,
                "intrusion": is_intrusion,
            }
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
        "people": counts["people"],
        "cars": counts["cars"],
        "buses": counts["buses"],
        "motorcycles": counts["motorcycles"],
        "fps": round(fps, 2),
        "line_crossings": people_crossed,
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
            "[WARNING] Analytics update error:",
            e,
        )


    # ========================================================
    # DATABASE
    # ========================================================

    save_analytics_record(
        analytics
    )


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
                "[WARNING] Crowd alert error:",
                e,
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
                "[WARNING] Traffic alert error:",
                e,
            )


    # ========================================================
    # UPDATE LATEST RESULT
    # ========================================================

    latest_result_data = {
        "people": counts["people"],
        "cars": counts["cars"],
        "buses": counts["buses"],
        "motorcycles": counts["motorcycles"],
        "fps": round(fps, 2),
        "line_crossings": people_crossed,
        "detections": detections,
        "intrusion": intrusion_detected,
    }


    with latest_result_lock:

        latest_result = (
            latest_result_data
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
            "[WARNING] Heatmap drawing error:",
            e,
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
            "[WARNING] "
            "Restricted zone drawing error:",
            e,
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
            "[WARNING] "
            "Line drawing error:",
            e,
        )


    # ========================================================
    # PEOPLE CROSSED
    # ========================================================

    cv2.putText(
        annotated,
        f"People Crossed: {people_crossed}",
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
        f"Cars Crossed: {cars_crossed}",
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
    # INTRUSION LABEL
    # ========================================================

    if intrusion_detected:

        cv2.putText(
            annotated,
            "!!! INTRUSION DETECTED !!!",
            (
                20,
                annotated.shape[0] - 30,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3,
        )


    # ========================================================
    # JPEG
    # ========================================================

    success, buffer = cv2.imencode(
        ".jpg",
        annotated,
    )


    if not success:

        return None


    return buffer.tobytes()


# ============================================================
# PROCESS REACT LIVE CAMERA FRAME
# ============================================================

def process_camera_frame(frame):

    """
    Process a frame coming directly from the React laptop
    webcam.

    Unlike process_frame(), this function returns JSON-safe
    detection coordinates so the React UI can draw bounding
    boxes over the browser camera.
    """

    start_time = time.time()


    # ========================================================
    # YOLO
    # ========================================================

    try:

        results = detect_and_track(
            frame
        )

    except Exception as e:

        print(
            "[ERROR] Camera YOLO error:",
            e,
        )

        return {
            "people": 0,
            "cars": 0,
            "buses": 0,
            "motorcycles": 0,
            "fps": 0.0,
            "line_crossings": 0,
            "detections": [],
            "intrusion": False,
        }


    if not results:

        return {
            "people": 0,
            "cars": 0,
            "buses": 0,
            "motorcycles": 0,
            "fps": 0.0,
            "line_crossings": 0,
            "detections": [],
            "intrusion": False,
        }


    result = results[0]

    names = result.names


    # ========================================================
    # COUNTS
    # ========================================================

    counts = {
        "people": 0,
        "cars": 0,
        "buses": 0,
        "motorcycles": 0,
    }


    detections = []

    intrusion_detected = False


    # ========================================================
    # PROCESS OBJECTS
    # ========================================================

    for box in result.boxes:

        try:

            cls = int(
                box.cls[0]
            )

            label = names[cls]

            confidence = float(
                box.conf[0]
            )

        except Exception:

            continue


        # ----------------------------------------------------
        # COUNTS
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
        # BOX
        # ----------------------------------------------------

        try:

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

        except Exception:

            continue


        # ----------------------------------------------------
        # TRACK ID
        # ----------------------------------------------------

        track_id = None

        if box.id is not None:

            try:

                track_id = int(
                    box.id[0]
                )

            except Exception:

                track_id = None


        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        center_x = int(
            (x1 + x2) / 2
        )

        center_y = int(
            (y1 + y2) / 2
        )


        # ====================================================
        # INTRUSION
        # ====================================================

        is_intrusion = False


        if label == "person":

            try:

                is_intrusion = (
                    restricted_zone.contains(
                        center_x,
                        center_y,
                    )
                )

            except Exception:

                is_intrusion = False


            if is_intrusion:

                intrusion_detected = True

                current_time = time.time()

                last_time = (
                    last_intrusion_time.get(
                        track_id,
                        0,
                    )
                )


                if (
                    track_id is not None
                    and
                    (
                        current_time
                        - last_time
                    )
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
                            "Intrusion screenshot error:",
                            e,
                        )


                    last_intrusion_time[
                        track_id
                    ] = current_time


                    try:

                        add_alert(
                            "🚨 Intrusion Detected! "
                            f"Screenshot: {filename}"
                        )

                    except Exception as e:

                        print(
                            "[WARNING] Alert error:",
                            e,
                        )


                    print(
                        "[ALERT] Live camera intrusion:",
                        filepath,
                    )


        # ====================================================
        # LINE COUNTER
        # ====================================================

        if track_id is not None:

            try:

                line_counter.update(
                    track_id,
                    label,
                    center_y,
                )

            except Exception as e:

                print(
                    "[WARNING] "
                    "Camera line counter error:",
                    e,
                )


        # ====================================================
        # FRONTEND DETECTION
        # ====================================================

        detections.append(
            {
                "class": label,
                "confidence": round(
                    confidence,
                    3,
                ),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "track_id": track_id,
                "intrusion": is_intrusion,
            }
        )


    # ========================================================
    # FPS
    # ========================================================

    elapsed = (
        time.time() - start_time
    )


    fps = (
        1 / elapsed
        if elapsed > 0
        else 0.0
    )


    # ========================================================
    # LINE CROSSINGS
    # ========================================================

    people_crossed = (
        line_counter.people_crossed
    )


    # ========================================================
    # ANALYTICS
    # ========================================================

    analytics = {
        "people": counts["people"],
        "cars": counts["cars"],
        "buses": counts["buses"],
        "motorcycles": counts["motorcycles"],
        "fps": round(fps, 2),
        "line_crossings": people_crossed,
    }


    # ========================================================
    # UPDATE ANALYTICS SERVICE
    # ========================================================

    try:

        update(
            analytics
        )

    except Exception as e:

        print(
            "[WARNING] "
            "Camera analytics update error:",
            e,
        )


    # ========================================================
    # SAVE TO DATABASE
    # ========================================================

    save_analytics_record(
        analytics
    )


    # ========================================================
    # UPDATE GLOBAL RESULT
    # ========================================================

    global latest_result

    latest_result_data = {
        "people": counts["people"],
        "cars": counts["cars"],
        "buses": counts["buses"],
        "motorcycles": counts["motorcycles"],
        "fps": round(fps, 2),
        "line_crossings": people_crossed,
        "detections": detections,
        "intrusion": intrusion_detected,
    }


    with latest_result_lock:

        latest_result = (
            latest_result_data
        )


    # ========================================================
    # RETURN JSON
    # ========================================================

    return latest_result_data


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
        # READ
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


            if not reopen_camera():

                time.sleep(
                    1
                )


            continue


        # ====================================================
        # PROCESS
        # ====================================================

        frame_bytes = process_frame(
            frame
        )


        if frame_bytes is None:

            continue


        # ====================================================
        # MJPEG
        # ====================================================

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: "
            +
            str(
                len(frame_bytes)
            ).encode()
            +
            b"\r\n\r\n"
            +
            frame_bytes
            +
            b"\r\n"
        )