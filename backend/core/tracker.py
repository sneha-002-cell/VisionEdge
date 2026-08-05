from ultralytics import YOLO

model = YOLO("yolo11n.pt")


def detect_and_track(frame):
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml"
    )

    return results