import cv2


class VideoStream:

    def __init__(self, source=0):
        """
        source can be:
        0 -> default webcam
        "video.mp4" -> video file
        RTSP URL -> IP camera (later)
        """
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception(f"Could not open source: {source}")

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()