from ultralytics import YOLO


# ============================================================
# YOLO MODEL
# ============================================================

model = YOLO("yolo11n.pt")


# ============================================================
# DETECTION + TRACKING
# ============================================================

def detect_and_track(frame):
    """
    Run YOLO object detection and ByteTrack tracking.

    Returns:
        Ultralytics Results list
    """

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False,
    )

    return results