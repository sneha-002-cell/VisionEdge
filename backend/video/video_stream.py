import cv2


class VideoStream:

    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception("Cannot open video.")

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()