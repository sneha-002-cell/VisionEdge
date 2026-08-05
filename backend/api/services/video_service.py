import cv2
import time
from ultralytics import YOLO

from backend.api.services.analytics_service import update
from backend.api.services.alert_service import add_alert
from backend.database.database import SessionLocal
from backend.database.crud import save_record
from backend.core.tracker import detect_and_track
from backend.core.heatmap import Heatmap
from backend.core.line_counter import LineCounter
from backend.core.restricted_zone import RestrictedZone

# ------------------------------------
# Initialize
# ------------------------------------
model = YOLO("yolo11n.pt")
camera = cv2.VideoCapture(0)

heatmap = Heatmap()
line_counter = LineCounter()
restricted_zone = RestrictedZone()

prev_time = time.time()


def generate_frames():
    global prev_time

    while True:

        success, frame = camera.read()

        if not success:
            break

        # ----------------------------
        # FPS
        # ----------------------------
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # ----------------------------
        # Detection + Tracking
        # ----------------------------
        results = detect_and_track(frame)

        names = model.names

        counts = {
            "people": 0,
            "cars": 0,
            "buses": 0,
            "motorcycles": 0,
        }

        # ----------------------------
        # Heatmap
        # ----------------------------
        boxes = results[0].boxes.xyxy.cpu().numpy()

        if len(boxes) > 0:
            heatmap.update(frame, boxes)

        # ----------------------------
        # Count Objects
        # ----------------------------
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

            # ----------------------------
            # Tracking
            # ----------------------------
            if box.id is not None:

                track_id = int(box.id[0])

                x1, y1, x2, y2 = box.xyxy[0]

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # Line Counter
                line_counter.update(
                    track_id,
                    label,
                    center_y,
                )

                # Restricted Zone
                if (
                    label == "person"
                    and restricted_zone.contains(center_x, center_y)
                ):
                    add_alert("🚨 Intrusion Detected!")

        # ----------------------------
        # Analytics
        # ----------------------------
        analytics = {
            "people": counts["people"],
            "cars": counts["cars"],
            "buses": counts["buses"],
            "motorcycles": counts["motorcycles"],
            "fps": round(fps, 2),
            "line_crossings": line_counter.people_crossed,
        }

        update(analytics)

        # ----------------------------
        # Save Database
        # ----------------------------
        db = SessionLocal()

        save_record(db, analytics)

        db.close()

        # ----------------------------
        # Alerts
        # ----------------------------
        if counts["people"] >= 3:
            add_alert(
                f"Crowd Alert: {counts['people']} people detected"
            )

        if counts["cars"] >= 5:
            add_alert(
                f"Traffic Alert: {counts['cars']} cars detected"
            )

        # ----------------------------
        # Draw detections
        # ----------------------------
        annotated = results[0].plot()

        # Heatmap
        annotated = heatmap.draw(annotated)

        # Restricted Zone
        annotated = restricted_zone.draw(annotated)

        # Counting Line
        cv2.line(
            annotated,
            (0, line_counter.line_y),
            (annotated.shape[1], line_counter.line_y),
            (0, 255, 255),
            3,
        )

        # People Crossed
        cv2.putText(
            annotated,
            f"People Crossed: {line_counter.people_crossed}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        # Cars Crossed
        cv2.putText(
            annotated,
            f"Cars Crossed: {line_counter.cars_crossed}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2,
        )

        # FPS
        cv2.putText(
            annotated,
            f"FPS: {round(fps,1)}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # ----------------------------
        # Encode
        # ----------------------------
        _, buffer = cv2.imencode(".jpg", annotated)
        frame_bytes = buffer.tobytes()

        # ----------------------------
        # Stream
        # ----------------------------
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )