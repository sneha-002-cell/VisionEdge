from ultralytics import YOLO

# Load pretrained model
model = YOLO("yolo11n.pt")

# Run object detection
results = model.predict(
    source="assets/images/test.jpg",
    save=True,
    conf=0.5
)

print("Detection completed successfully!")