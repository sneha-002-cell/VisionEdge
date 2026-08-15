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

# Render environment variable can override settings.py
VIDEO_SOURCE_ENV = os.getenv(
    "VIDEO_SOURCE",
    VIDEO_SOURCE
)


def get_video_source():
    """
    Convert VIDEO_SOURCE into a usable OpenCV source.

    Supported examples:

        0
        "0"
        "assets/videos/traffic.mp4"
        "rtsp://username:password@ip:554/stream"
        "https://example.com/video.mp4"
    """

    source = VIDEO_SOURCE_ENV

    # Direct integer webcam index
    if isinstance(source, int):
        return source

    if isinstance(source, str):

        source = source.strip()

        # Environment variable such as VIDEO_SOURCE=0
        if source.isdigit():
            return int(source)

        # Remote sources should not be modified
        if source.startswith(
            (
                "rtsp://",
                "http://",
                "https://"
            )
        ):
            return source

        # Convert local relative path to absolute path
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
# VIDEO INITIALIZATION
# ============================================================

camera = cv2.VideoCapture(
    VIDEO_SOURCE_VALUE
)


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
# VISIONEDGE ANALYTICS COMPONENTS
# ============================================================

heatmap = Heatmap()

line_counter = LineCounter()

restricted_zone = RestrictedZone()

prev_time = time.time()


# ============================================================
# INTRUSION DETECTION SETTINGS
# ============================================================

last_intrusion_time = {}

INTRUSION_COOLDOWN = 10


# ============================================================
# VIDEO FRAME GENERATOR
# ============================================================

def generate_frames():

    global prev_time

    while True:

        # ----------------------------------------------------
        # Read frame
        # ----------------------------------------------------

        success, frame = camera.read()


        # ----------------------------------------------------
        # Restart prerecorded video at EOF
        # ----------------------------------------------------

        if not success:

            # Only restart file/video sources.
            # Do not attempt to restart a webcam.
            if isinstance(
                VIDEO_SOURCE_VALUE,
                str
            ):

                print(
                    "[INFO] Video reached end. "
                    "Restarting from beginning..."
                )

                camera.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                success, frame = camera.read()


            # If frame still cannot be read,
            # stop the stream safely.
            if not success:

                print(
                    "[ERROR] Could not read frame "
                    "from video source."
                )

                break


        # ====================================================
        # FPS CALCULATION
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

        # IMPORTANT:
        #
        # detect_and_track() already performs YOLO inference.
        #
        # We therefore DO NOT load another YOLO model here.
        #
        # This avoids duplicate model loading and fixes the
        # Render deployment issue caused by model = YOLO(...).
        #

        results = detect_and_track(
            frame
        )


        # Get class names directly from YOLO results
        names = results[0].names


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

        boxes = (
            results[0]
            .boxes
            .xyxy
            .cpu()
            .numpy()
        )

        if len(boxes) > 0:

            heatmap.update(
                frame,
                boxes
            )


        # ====================================================
        # PROCESS DETECTED OBJECTS
        # ====================================================

        for box in results[0].boxes:

            # ------------------------------------------------
            # Class
            # ------------------------------------------------

            cls = int(
                box.cls[0]
            )

            label = names[cls]


            # ------------------------------------------------
            # Object counting
            # ------------------------------------------------

            if label == "person":

                counts["people"] += 1

            elif label == "car":

                counts["cars"] += 1

            elif label == "bus":

                counts["buses"] += 1

            elif label == "motorcycle":

                counts["motorcycles"] += 1


            # =================================================
            # TRACKING
            # =================================================

            if box.id is None:
                continue


            track_id = int(
                box.id[0]
            )


            # ------------------------------------------------
            # Bounding box center
            # ------------------------------------------------

            x1, y1, x2, y2 = box.xyxy[0]

            center_x = int(
                (x1 + x2) / 2
            )

            center_y = int(
                (y1 + y2) / 2
            )


            # =================================================
            # LINE CROSSING
            # =================================================

            line_counter.update(
                track_id,
                label,
                center_y
            )


            # =================================================
            # RESTRICTED ZONE / INTRUSION
            # =================================================

            if (
                label == "person"
                and restricted_zone.contains(
                    center_x,
                    center_y
                )
            ):

                current_time = time.time()

                last_time = (
                    last_intrusion_time.get(
                        track_id,
                        0
                    )
                )


                # Cooldown prevents saving an image
                # on every single frame.
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


                    # Save intrusion frame
                    cv2.imwrite(
                        filepath,
                        frame
                    )


                    # Update cooldown
                    last_intrusion_time[
                        track_id
                    ] = current_time


                    # Create VisionEdge alert
                    add_alert(
                        f"🚨 Intrusion Detected! "
                        f"Screenshot: {filename}"
                    )


                    print(
                        "[ALERT] Intrusion screenshot "
                        f"saved: {filepath}"
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
                round(fps, 2),

            "line_crossings":
                line_counter.people_crossed,
        }


        update(
            analytics
        )


        # ====================================================
        # SAVE ANALYTICS TO DATABASE
        # ====================================================

        db = SessionLocal()

        try:

            save_record(
                db,
                analytics
            )

        finally:

            db.close()


        # ====================================================
        # CROWD ALERT
        # ====================================================

        if counts["people"] >= 3:

            add_alert(
                f"Crowd Alert: "
                f"{counts['people']} people detected"
            )


        # ====================================================
        # TRAFFIC ALERT
        # ====================================================

        if counts["cars"] >= 5:

            add_alert(
                f"Traffic Alert: "
                f"{counts['cars']} cars detected"
            )


        # ====================================================
        # DRAW YOLO DETECTIONS
        # ====================================================

        annotated = results[0].plot()


        # ====================================================
        # DRAW HEATMAP
        # ====================================================

        annotated = heatmap.draw(
            annotated
        )


        # ====================================================
        # DRAW RESTRICTED ZONE
        # ====================================================

        annotated = restricted_zone.draw(
            annotated
        )


        # ====================================================
        # DRAW COUNTING LINE
        # ====================================================

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
        # JPEG ENCODING
        # ====================================================

        success, buffer = cv2.imencode(
            ".jpg",
            annotated
        )

        if not success:

            continue


        frame_bytes = buffer.tobytes()


        # ====================================================
        # MJPEG STREAM
        # ====================================================

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )