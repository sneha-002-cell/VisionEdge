class LineCounter:
    def __init__(self, line_y=300):
        self.line_y = line_y
        self.crossed_ids = set()
        self.count = 0

    def update(self, track_id, center_y):
        """
        Count an object only once when it crosses the line.
        """
        if center_y > self.line_y and track_id not in self.crossed_ids:
            self.crossed_ids.add(track_id)
            self.count += 1

        return self.count