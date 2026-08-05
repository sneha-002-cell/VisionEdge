import cv2
import numpy as np


class Heatmap:

    def __init__(self):
        self.map = None

    def update(self, frame, boxes):

        if self.map is None:
            self.map = np.zeros(
                frame.shape[:2],
                dtype=np.float32
            )

        for box in boxes:

            x1, y1, x2, y2 = map(int, box)

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            cv2.circle(
                self.map,
                (cx, cy),
                20,
                1,
                -1
            )

    def draw(self, frame):

        heat = cv2.GaussianBlur(
            self.map,
            (0, 0),
            25
        )

        heat = cv2.normalize(
            heat,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        colored = cv2.applyColorMap(
            heat,
            cv2.COLORMAP_JET
        )

        return cv2.addWeighted(
            frame,
            0.7,
            colored,
            0.3,
            0
        )