from ultralytics import YOLO


class YOLODetector:

    def __init__(self, model_path="yolo11n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        return self.model(frame)