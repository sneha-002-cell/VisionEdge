import time


class FPSCounter:
    def __init__(self):
        self.prev_time = time.time()
        self.fps = 0

    def update(self):
        current_time = time.time()

        self.fps = 1 / (current_time - self.prev_time)

        self.prev_time = current_time

        return self.fps