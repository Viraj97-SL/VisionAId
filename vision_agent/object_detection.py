import cv2
import time
from collections import defaultdict
from ultralytics import YOLO
from core.utils import speak
import zmq
import threading


class ObjectDetectionAgent:
    def __init__(self):
        self.MAX_RUNTIME = 120  # Maximum runtime in seconds
        self.COOLDOWN_SEC = 15  # Cooldown between announcements
        self.running = False  # Initialize as False, set to True when running
        self.model = YOLO("../yolov8n.pt")
        self.last_spoken = defaultdict(float)
        self.camera = cv2.VideoCapture(0)
        self.lock = threading.Lock()

        # MCP Setup
        self.context = zmq.Context()
        self.mcp_socket = self.context.socket(zmq.PUB)
        self.mcp_socket.connect("tcp://localhost:5555")

    def run(self):
        """Main execution method that MasterAgent will call"""
        self.running = True
        start_time = time.time()

        try:
            while self.running and (time.time() - start_time) < self.MAX_RUNTIME:
                ret, frame = self.camera.read()
                if not ret:
                    speak("Camera error occurred")
                    break

                # Perform object detection
                results = self.model(frame)
                detected_objects = set()

                for result in results:
                    for box in result.boxes:
                        class_id = int(box.cls)
                        detected_objects.add(result.names[class_id])

                # Announce and publish new detections
                if detected_objects:
                    with self.lock:
                        self._announce_objects(detected_objects)

                # Display results
                self._display_frame(frame, results)

                # Check for exit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            speak(f"Object detection error: {str(e)}")
        finally:
            self.terminate()

    def _display_frame(self, frame, results):
        """Display the frame with detection results"""
        annotated_frame = results[0].plot()
        cv2.putText(annotated_frame, "Object Detection", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(annotated_frame, "Press 'q' to quit", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Object Detection", annotated_frame)

    def _announce_objects(self, objects):
        """Handle object announcement and MCP publishing"""
        now = time.time()
        for obj in objects:
            if now - self.last_spoken[obj] > self.COOLDOWN_SEC:
                # MCP Integration
                self._publish_to_mcp(objects)

                # Existing functionality
                speak(f"I see a {obj}")
                self.last_spoken[obj] = now

    def _publish_to_mcp(self, objects):
        """Send detection results to MCP"""
        self.mcp_socket.send_json({
            "source": "vision",
            "agent": "object",
            "data": {
                "objects": list(objects),
                "count": len(objects)
            },
            "timestamp": time.time()
        })

    def terminate(self):
        """Clean up resources - called by MasterAgent during shutdown"""
        self.running = False
        if hasattr(self, 'camera') and self.camera.isOpened():
            self.camera.release()
        cv2.destroyAllWindows()
        if hasattr(self, 'mcp_socket'):
            self.mcp_socket.close()
        if hasattr(self, 'context'):
            self.context.term()

if __name__ == "__main__":
    # For standalone testing
    agent = ObjectDetectionAgent()
    agent.run()
