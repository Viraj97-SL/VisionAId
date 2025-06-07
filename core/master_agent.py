import cv2
import time
import zmq
import threading
import numpy as np
from agents.vision_agent.barcode_reader import BarcodeReaderAgent
from agents.ecommerce_agent.ecommerce_agent import EcommerceAgent
from agents.vision_agent.object_detection import ObjectDetectionAgent
from agents.vision_agent.document_ocr import DocumentOCRAgent
from agents.navigation.navigation_agent import NavigationAgent
from agents.vision_agent.emotion_detection_agent import EmotionDetectionAgent
from core.utils import speak
from threading import Thread
from core.mcp_logger import MCPLogger



class MasterAgent:
    def __init__(self):
        # Initialize all sub-agents
        self.agents = {
            "object_detection": ObjectDetectionAgent(),
            "barcode_scanner": BarcodeReaderAgent(),
            "document_reader": DocumentOCRAgent(),
            "navigation": NavigationAgent(),
            "ecommerce_agent": EcommerceAgent(),
            "emotion_detection_agent": EmotionDetectionAgent()
        }

        self.current_agent = None
        self.running = True
        self.agent_busy = False
        self.logger = MCPLogger()

        # Visual feedback settings
        self.display_help = True
        self.last_switch_time = 0
        self.help_cooldown = 5  # seconds

        # Thread safety
        self.lock = threading.Lock()

        # MCP Integration
        self._start_vision_listener()
        self.message_queue = []
        self.last_messages = {}

    def _start_vision_listener(self):
        """Start ZeroMQ listener in a background thread"""

        def _listen():
            context = zmq.Context()
            subscriber = context.socket(zmq.SUB)
            subscriber.bind("tcp://*:5555")
            subscriber.setsockopt_string(zmq.SUBSCRIBE, '')

            while self.running:
                try:
                    msg = subscriber.recv_json()
                    with self.lock:
                        self._handle_vision_message(msg)
                except zmq.ZMQError as e:
                    if self.running:
                        speak(f"Communication error: {str(e)}")
                        self.logger.log_error(f"ZMQ Error: {str(e)}")
                except Exception as e:
                    error_msg = f"Message handling error: {str(e)}"
                    print(error_msg)
                    self.logger.log_error(error_msg)

        Thread(target=_listen, daemon=True).start()

    def _handle_vision_message(self, msg):
        """Process incoming messages from agents"""
        try:
            if not isinstance(msg, dict):
                raise ValueError("Invalid message format")

            agent_type = msg.get("agent", "unknown")
            data = msg.get("data", {})
            timestamp = msg.get("timestamp", time.time())

            # Store last message from each agent
            self.last_messages[agent_type] = {
                "data": data,
                "timestamp": timestamp
            }

            # Log to database
            self.logger.insert_message({
                "agent": agent_type,
                "data": data,
                "timestamp": timestamp
            })

            # Agent-specific processing
            if agent_type == "barcode":
                product = data.get("product", "unknown product")
                speak(f"Barcode scanned: {product}")

            elif agent_type == "document":
                text = data.get("text", "")[:100]  # First 100 chars
                speak(f"Document text recognized: {text}")

            elif agent_type == "object":
                objects = data.get("objects", [])
                if objects:
                    speak(f"Detected objects: {', '.join(objects[:3])}")

            elif agent_type == "emotion":
                emotion = data.get("top_emotion", "unknown")
                confidence = data.get("confidence", 0)
                speak(f"Detected emotion: {emotion} ({(confidence * 100):.1f}% confidence)")

        except Exception as e:
            error_msg = f"Error handling message: {str(e)}"
            print(error_msg)
            self.logger.log_error(error_msg)

    def run(self):
        try:
            while self.running:
                self.display_status()

                # Process any queued messages
                with self.lock:
                    if self.message_queue:
                        msg = self.message_queue.pop(0)
                        self._handle_vision_message(msg)

                # Press Q to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.shutdown()
                    break

        except Exception as e:
            speak(f"System error: {str(e)}")
            raise
        finally:
            self.cleanup()

    def switch_agent(self, agent_name):
        with self.lock:
            try:
                if self.current_agent:
                    self.current_agent.terminate()
                    time.sleep(0.5)

                self.current_agent = self.agents.get(agent_name)
                if not self.current_agent:
                    speak("Unknown agent requested.")
                    return

                speak(f"Switched to {agent_name.replace('_', ' ')}")
                self.last_switch_time = time.time()

                if hasattr(self.current_agent, 'run_non_blocking'):
                    self.current_agent.run_non_blocking()
                else:
                    self.current_agent.run()

            except Exception as e:
                speak(f"Failed to switch agents: {str(e)}")

    def display_status(self):
        overlay = np.zeros((350, 700, 3), dtype=np.uint8)  # Slightly larger window

        # Current agent status
        if self.current_agent:
            status_text = f"Active: {type(self.current_agent).__name__}"
            cv2.putText(overlay, status_text, (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Last messages display
        y_offset = 120
        cv2.putText(overlay, "Last Events:", (50, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        for agent, info in self.last_messages.items():
            y_offset += 30
            elapsed = time.time() - info['timestamp']
            summary = self._summarize_message(agent, info['data'])
            text = f"{agent.replace('_', ' ')}: {summary} ({elapsed:.1f}s ago)"
            cv2.putText(overlay, text, (50, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)

        # Help commands (when needed)
        if not self.current_agent or time.time() - self.last_switch_time < self.help_cooldown:
            y_offset += 50
            help_text = "Voice Commands:"
            cv2.putText(overlay, help_text, (50, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

            commands = [
                "'Object detection'",
                "'Scan barcode'",
                "'Read document'",
                "'Navigate'",
                "'Ecommerce'",
                "'Exit'",
                "'emotion detection'"
            ]

            for i, cmd in enumerate(commands):
                cv2.putText(overlay, cmd, (50, y_offset + 30 + i * 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

        cv2.imshow("VisionAI Control", overlay)

    def _summarize_message(self, agent, data):
        """Create a short summary of agent messages"""
        if agent == "barcode":
            return data.get("code", "no code")[:10]
        elif agent == "document":
            return f"{len(data.get('text', ''))} chars"
        elif agent == "object":
            return f"{len(data.get('objects', []))} objects"
        return "activity detected"

    def shutdown(self):
        speak("Shutting down all systems")
        self.running = False
        self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        for agent in self.agents.values():
            if hasattr(agent, 'terminate'):
                agent.terminate()
        cv2.destroyAllWindows()
        self.logger.close_connection()


if __name__ == "__main__":
    master = MasterAgent()
    try:
        master.run()
    except KeyboardInterrupt:
        pass
    finally:
        master.cleanup()
