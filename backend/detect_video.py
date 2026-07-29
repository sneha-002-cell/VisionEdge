from ultralytics import YOLO
import cv2

# Load the YOLO model
model = YOLO("yolo11n.pt")

# Open the video
video_path = "assets/videos/traffic.mp4"
cap = cv2.VideoCapture(video_path)

# Check if video opened
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:

    # Read one frame
    success, frame = cap.read()

    if not success:
        break

    # Run YOLO
    results = model(frame)

    # Draw detections
    annotated_frame = results[0].plot()

    # Display frame
    cv2.imshow("VisionEdge", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()