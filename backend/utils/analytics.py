class Analytics:

    @staticmethod
    def count_objects(results):
        """
        Count the number of detected objects by class.
        """
        counts = {}

        boxes = results[0].boxes

        for box in boxes:
            class_id = int(box.cls)
            class_name = results[0].names[class_id]

            counts[class_name] = counts.get(class_name, 0) + 1

        return counts