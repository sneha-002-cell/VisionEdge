class LineCounter:
    def __init__(self):
        # Position of the counting line
        self.line_y = 250

        # Store previous Y position of tracked objects
        self.previous_positions = {}

        # IDs that have already crossed
        self.crossed_ids = set()

        self.people_crossed = 0
        self.cars_crossed = 0

    def update(self, track_id, class_name, center_y):
        # First time seeing this object
        if track_id not in self.previous_positions:
            self.previous_positions[track_id] = center_y
            return

        previous_y = self.previous_positions[track_id]

        # Crossing condition
        if (
            previous_y < self.line_y
            and center_y >= self.line_y
            and track_id not in self.crossed_ids
        ):
            self.crossed_ids.add(track_id)

            if class_name == "person":
                self.people_crossed += 1

            elif class_name == "car":
                self.cars_crossed += 1

        # Update last position
        self.previous_positions[track_id] = center_y