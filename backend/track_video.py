from ultralytics import YOLO
import cv2

# Load model
model = YOLO("yolo11n.pt")

# Open video
cap = cv2.VideoCapture("assets/videos/traffic.mp4")

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    # Detection + Tracking
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml"
    )

    annotated_frame = results[0].plot()

    cv2.imshow("VisionEdge Tracking", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()