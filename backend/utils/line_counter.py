from config.settings import COUNTING_LINE_Y


class LineCounter:
    def __init__(self):
        self.line_y = COUNTING_LINE_Y
        self.crossed_ids = set()
        self.count = 0

    def update(self, track_id, center_y):
        if center_y > self.line_y and track_id not in self.crossed_ids:
            self.crossed_ids.add(track_id)
            self.count += 1

        return self.count