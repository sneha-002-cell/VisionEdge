from fastapi import APIRouter, UploadFile, File
from ultralytics import YOLO
import cv2
import numpy as np

router = APIRouter()

# Load YOLO model only once
model = YOLO("yolov8n.pt")


@router.post("/detect-image")
async def detect_image(file: UploadFile = File(...)):
    # Read uploaded image
    contents = await file.read()

    # Convert bytes to NumPy array
    np_array = np.frombuffer(contents, np.uint8)

    # Decode image
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Run YOLO detection
    results = model(image)

    detections = []

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        detections.append({
            "class": model.names[class_id],
            "confidence": round(confidence, 3)
        })

    return {
        "filename": file.filename,
        "total_objects": len(detections),
        "detections": detections
    }