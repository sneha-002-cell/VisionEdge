import cv2


class RestrictedZone:
    def __init__(self):
        # Rectangle coordinates
        self.x1 = 50
        self.y1 = 300
        self.x2 = 300
        self.y2 = 470

    def draw(self, frame):
        cv2.rectangle(
            frame,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (0, 0, 255),
            2,
        )

        cv2.putText(
            frame,
            "RESTRICTED AREA",
            (self.x1, self.y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        return frame

    def contains(self, x, y):
        return (
            self.x1 <= x <= self.x2
            and self.y1 <= y <= self.y2
        )