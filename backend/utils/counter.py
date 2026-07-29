class ObjectCounter:
    def __init__(self):
        self.count = 0
        self.counted_ids = set()

    def update(self, track_ids):
        """
        Count each tracked object only once.
        """
        for track_id in track_ids:
            if track_id not in self.counted_ids:
                self.counted_ids.add(track_id)
                self.count += 1

        return self.count