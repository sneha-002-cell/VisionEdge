import cv2

from streaming.video_stream import VideoStream
from inference.yolo_detector import YOLODetector
from utils.visualizer import Visualizer
from utils.fps_counter import FPSCounter
from utils.analytics import Analytics
from utils.counter import ObjectCounter
from utils.line_counter import LineCounter
from config.settings import WINDOW_NAME


def main():
    # Initialize video stream
    from config.settings import VIDEO_SOURCE

    stream = VideoStream(VIDEO_SOURCE)

    # Load YOLO detector (with tracking enabled)
    detector = YOLODetector()

    # Initialize FPS counter
    fps_counter = FPSCounter()

    # Initialize Object Counter
    counter = ObjectCounter()

    # Initialize Line Counter
    line_counter = LineCounter()

    while True:
        # Read a frame
        success, frame = stream.read()

        if not success:
            break

        # Run object detection + tracking
        results = detector.detect(frame)

        # Extract tracking IDs
        track_ids = []

        # Check if tracking IDs are available
        if results[0].boxes.id is not None:

            boxes = results[0].boxes
            track_ids = boxes.id.int().cpu().tolist()

            # Check every tracked object
            for box, track_id in zip(boxes.xyxy, track_ids):

                # Bounding box coordinates
                x1, y1, x2, y2 = box.tolist()

                # Calculate center of object
                center_y = (y1 + y2) / 2

                # Update line counter
                line_counter.update(track_id, center_y)

        # Count unique tracked objects
        total_count = counter.update(track_ids)

        # Count detected objects by class
        counts = Analytics.count_objects(results)

        # Calculate FPS
        fps = fps_counter.update()

        # Current line crossing count
        line_count = line_counter.count

        # Draw dashboard
        output = Visualizer.draw(
            results,
            fps,
            counts,
            total_count,
            line_count
        )

        # Display output
        cv2.imshow(WINDOW_NAME, output)

        # Exit on Q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release resources
    stream.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()