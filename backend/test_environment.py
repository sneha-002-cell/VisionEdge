import cv2
import numpy as np
from ultralytics import YOLO

print("=" * 50)
print("VisionEdge Environment Test")
print("=" * 50)

print("OpenCV Version :", cv2.__version__)
print("NumPy Version  :", np.__version__)

model = YOLO("yolo11n.pt")

print("YOLO Model Loaded Successfully!")
print("=" * 50)