import cv2


class Visualizer:

    @staticmethod
    def draw(results, fps, counts, total_count, line_count):

        # Draw YOLO detections
        frame = results[0].plot()

        # Draw the counting line
        cv2.line(
            frame,
            (0, 300),
            (frame.shape[1], 300),
            (0, 0, 255),
            3
        )

        # Draw dashboard background
        cv2.rectangle(
            frame,
            (10, 10),
            (350, 320),
            (40, 40, 40),
            -1
        )

        # Dashboard title
        cv2.putText(
            frame,
            "VisionEdge Analytics",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        y = 70

        # Display FPS
        cv2.putText(
            frame,
            f"FPS: {fps:.2f}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        y += 30

        # Display object counts
        for name, value in counts.items():
            cv2.putText(
                frame,
                f"{name.capitalize()}: {value}",
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            y += 30

        # Display total unique tracked objects
        cv2.putText(
            frame,
            f"Unique Objects: {total_count}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        y += 30

        # Display line crossing count
        cv2.putText(
            frame,
            f"Line Crossings: {line_count}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 165, 0),
            2
        )

        return frame