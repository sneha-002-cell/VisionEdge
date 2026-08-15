import cv2
import time
import os
from datetime import datetime

from ultralytics import YOLO

from backend.api.services.analytics_service import update
from backend.api.services.alert_service import add_alert
from backend.database.database import SessionLocal
from backend.database.crud import save_record
from backend.core.tracker import detect_and_track
from backend.core.heatmap import Heatmap
from backend.core.line_counter import LineCounter
from backend.core.restricted_zone import RestrictedZone
from backend.config.settings import VIDEO_SOURCE


# ------------------------------------
# Paths
# ------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

MODEL_PATH = os.path.join(BASE_DIR, "yolo11n.pt")

INCIDENT_FOLDER = os.path.join(
    BASE_DIR,
    "assets",
    "incidents"
)

os.makedirs(INCIDENT_FOLDER, exist_ok=True)


# ------------------------------------
# Video Source
# ------------------------------------

# Allow Render environment variable to override settings.py
VIDEO_SOURCE_ENV = os.getenv(
    "VIDEO_SOURCE",
    VIDEO_SOURCE
)


def get_video_source():
    """
    Convert VIDEO_SOURCE into a usable OpenCV source.

    Examples:
        0
        "0"
        "assets/videos/traffic.mp4"
        "rtsp://..."
    """

    source = VIDEO_SOURCE_ENV

    # Webcam index
    if isinstance(source, int):
        return source

    # Environment variables are strings
    if isinstance(source, str):

        source = source.strip()

        if source.isdigit():
            return int(source)

        # Convert relative paths to absolute paths
        if not source.startswith(("rtsp://", "http://", "https://")):

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


# ------------------------------------
# Initialize YOLO
# ------------------------------------

model = YOLO(MODEL_PATH)


# ------------------------------------
# Initialize Video
# ------------------------------------

camera = cv2.VideoCapture(
    VIDEO_SOURCE_VALUE
)

if not camera.isOpened():

    print(
        f"[ERROR] Could not open video source: "
        f"{VIDEO_SOURCE_VALUE}"
    )

else:

    print(
        f"[INFO] Video source opened successfully: "
        f"{VIDEO_SOURCE_VALUE}"
    )


# ------------------------------------
# Initialize VisionEdge Components
# ------------------------------------

heatmap = Heatmap()
line_counter = LineCounter()
restricted_zone = RestrictedZone()

prev_time = time.time()


# ------------------------------------
# Intrusion Screenshot Settings
# ------------------------------------

last_intrusion_time = {}

INTRUSION_COOLDOWN = 10


# ------------------------------------
# Generate Frames
# ------------------------------------

def generate_frames():

    global prev_time

    while True:

        success, frame = camera.read()

        # --------------------------------
        # Restart video when it reaches EOF
        # --------------------------------

        if not success:

            # For prerecorded video:
            # restart from the beginning

            if isinstance(VIDEO_SOURCE_VALUE, str):

                camera.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                success, frame = camera.read()

            if not success:

                print(
                    "[ERROR] Could not read frame "
                    "from video source."
                )

                break

        # --------------------------------
        # FPS
        # --------------------------------

        current_time = time.time()

        elapsed = current_time - prev_time

        if elapsed > 0:
            fps = 1 / elapsed
        else:
            fps = 0

        prev_time = current_time

        # --------------------------------
        # Detection + Tracking
        # --------------------------------

        results = detect_and_track(frame)

        names = model.names

        counts = {
            "people": 0,
            "cars": 0,
            "buses": 0,
            "motorcycles": 0,
        }

        # --------------------------------
        # Heatmap
        # --------------------------------

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

        # --------------------------------
        # Count Objects
        # --------------------------------

        for box in results[0].boxes:

            cls = int(box.cls[0])

            label = names[cls]

            if label == "person":

                counts["people"] += 1

            elif label == "car":

                counts["cars"] += 1

            elif label == "bus":

                counts["buses"] += 1

            elif label == "motorcycle":

                counts["motorcycles"] += 1

            # --------------------------------
            # Tracking
            # --------------------------------

            if box.id is not None:

                track_id = int(
                    box.id[0]
                )

                x1, y1, x2, y2 = box.xyxy[0]

                center_x = int(
                    (x1 + x2) / 2
                )

                center_y = int(
                    (y1 + y2) / 2
                )

                # --------------------------------
                # Line Counter
                # --------------------------------

                line_counter.update(
                    track_id,
                    label,
                    center_y,
                )

                # --------------------------------
                # Restricted Zone
                # --------------------------------

                if (
                    label == "person"
                    and restricted_zone.contains(
                        center_x,
                        center_y
                    )
                ):

                    current_time = time.time()

                    last_time = (
                        last_intrusion_time
                        .get(track_id, 0)
                    )

                    if (
                        current_time - last_time
                        >= INTRUSION_COOLDOWN
                    ):

                        timestamp = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
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

                        # Save intrusion screenshot
                        cv2.imwrite(
                            filepath,
                            frame
                        )

                        last_intrusion_time[
                            track_id
                        ] = current_time

                        # Add alert
                        add_alert(
                            f"🚨 Intrusion Detected! "
                            f"Screenshot: {filename}"
                        )

                        print(
                            "[ALERT] Intrusion screenshot "
                            f"saved: {filepath}"
                        )

        # --------------------------------
        # Analytics
        # --------------------------------

        analytics = {

            "people": counts["people"],

            "cars": counts["cars"],

            "buses": counts["buses"],

            "motorcycles": counts["motorcycles"],

            "fps": round(fps, 2),

            "line_crossings":
                line_counter.people_crossed,
        }

        update(
            analytics
        )

        # --------------------------------
        # Save Database
        # --------------------------------

        db = SessionLocal()

        try:

            save_record(
                db,
                analytics
            )

        finally:

            db.close()

        # --------------------------------
        # Alerts
        # --------------------------------

        if counts["people"] >= 3:

            add_alert(
                f"Crowd Alert: "
                f"{counts['people']} people detected"
            )

        if counts["cars"] >= 5:

            add_alert(
                f"Traffic Alert: "
                f"{counts['cars']} cars detected"
            )

        # --------------------------------
        # Draw YOLO Detections
        # --------------------------------

        annotated = results[0].plot()

        # --------------------------------
        # Heatmap
        # --------------------------------

        annotated = heatmap.draw(
            annotated
        )

        # --------------------------------
        # Restricted Zone
        # --------------------------------

        annotated = restricted_zone.draw(
            annotated
        )

        # --------------------------------
        # Counting Line
        # --------------------------------

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
            3,
        )

        # --------------------------------
        # People Crossed
        # --------------------------------

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
            2,
        )

        # --------------------------------
        # Cars Crossed
        # --------------------------------

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
            2,
        )

        # --------------------------------
        # FPS
        # --------------------------------

        cv2.putText(
            annotated,
            f"FPS: {round(fps, 1)}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # --------------------------------
        # Encode Frame
        # --------------------------------

        success, buffer = cv2.imencode(
            ".jpg",
            annotated
        )

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        # --------------------------------
        # Stream Frame
        # --------------------------------

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )