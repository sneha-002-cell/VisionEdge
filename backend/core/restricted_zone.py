import cv2


class RestrictedZone:

    def __init__(self):
        # ============================================================
        # RESTRICTED ZONE
        #
        # Coordinates are designed for the 640px-wide AI frame
        # sent from LiveCamera.jsx.
        #
        # Typical 16:9 frame:
        #     Width  = 640
        #     Height = 360
        # ============================================================

        self.x1 = 50
        self.y1 = 180

        self.x2 = 300
        self.y2 = 340

    # ============================================================
    # DRAW RESTRICTED ZONE
    # ============================================================

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
            (
                self.x1,
                max(self.y1 - 10, 20),
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        return frame

    # ============================================================
    # CHECK WHETHER POINT IS INSIDE RESTRICTED ZONE
    # ============================================================

    def contains(self, x, y):

        return (
            self.x1 <= x <= self.x2
            and
            self.y1 <= y <= self.y2
        )