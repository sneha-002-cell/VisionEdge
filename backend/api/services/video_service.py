import cv2
from ultralytics import YOLO
from backend.api.services.analytics_service import update

# Load YOLO model once
model = YOLO("yolo11n.pt")

# Open webcam
camera = cv2.VideoCapture(0)


def generate_frames():
    while True:
        success, frame = camera.read()

        if not success:
            break

        # Run YOLO detection
        results = model(frame)

        # Get class names
        names = model.names

        # Count detected objects
        counts = {
            "people": 0,
            "cars": 0,
            "buses": 0,
            "motorcycles": 0
        }

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

        # Update analytics
        update({
            "people": counts["people"],
            "cars": counts["cars"],
            "buses": counts["buses"],
            "motorcycles": counts["motorcycles"]
        })

        # Draw detections
        annotated = results[0].plot()

        # Encode frame as JPEG
        _, buffer = cv2.imencode(".jpg", annotated)
        frame_bytes = buffer.tobytes()

        # Yield frame for streaming
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes +
            b"\r\n"
        )