import cv2
import time
from collections import defaultdict
from ultralytics import YOLO
from core.utils import speak  # Use shared speak() from core utils
import pygame


class ObjectDetectionAgent:
    def __init__(self):
        # Configuration
        self.MAX_RUNTIME = 120
        self.COOLDOWN_SEC = 15
        self.running = True

        # Initialize components
        self.model = YOLO("yolov8n.pt")
        self.last_spoken = defaultdict(float)
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")

    def run(self):
        """Main execution loop to be called by master agent"""
        start_time = time.time()
        try:
            while self.running:
                # Runtime check
                if self._check_timeout(start_time):
                    break

                ret, frame = self.camera.read()
                if not ret:
                    speak("Camera frame read failed")
                    break

                processed_frame = self._process_frame(frame)
                cv2.imshow("Object Detection", processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            speak(f"Object detection error: {str(e)}")
        finally:
            self.terminate()

    def _check_timeout(self, start_time):
        """Handle max runtime logic"""
        if self.MAX_RUNTIME > 0 and (time.time() - start_time) > self.MAX_RUNTIME:
            speak("Object detection time completed")
            return True
        return False

    def _process_frame(self, frame):
        """Detect objects and annotate frame"""
        results = self.model.predict(frame, conf=0.5, verbose=False)
        current_objects = set()

        for result in results:
            for box in result.boxes:
                label = self.model.names[int(box.cls)]
                current_objects.add(label)
                self._draw_boxes(frame, box, label)

        self._announce_objects(current_objects)
        return frame

    def _draw_boxes(self, frame, box, label):
        """Draw bounding boxes and labels"""
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {box.conf.item():.2f}",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (0, 255, 0), 2)

    def _announce_objects(self, objects):
        """Handle audio announcements with cooldown"""
        now = time.time()
        for obj in objects:
            if now - self.last_spoken[obj] > self.COOLDOWN_SEC:
                speak(f"I see a {obj}")
                self.last_spoken[obj] = now

    def terminate(self):
        """Cleanup for master agent control"""
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # For standalone testing
    agent = ObjectDetectionAgent()
    agent.run()

