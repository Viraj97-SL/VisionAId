import cv2
import time
from agents.barcode_reader import BarcodeReaderAgent
from agents.ecommerce_agent.ecommerce_agent import EcommerceAgent
from agents.object_detection import ObjectDetectionAgent
from agents.document_ocr import DocumentOCRAgent
from agents.navigation.navigation_agent import NavigationAgent
from core.utils import speak
import numpy as np
import threading


class MasterAgent:
    def __init__(self):
        # Initialize all sub-agents
        self.agents = {
            "object_detection": ObjectDetectionAgent(),
            "barcode_scanner": BarcodeReaderAgent(),
            "document_reader": DocumentOCRAgent(),
            "navigation": NavigationAgent(),
            "ecommerce_agent": EcommerceAgent()
        }

        self.current_agent = None
        self.running = True

        self.agent_busy = False

        # Visual feedback settings
        self.display_help = True
        self.last_switch_time = 0
        self.help_cooldown = 5  # seconds

        # Thread safety
        self.lock = threading.Lock()

    def run(self):
        try:
            while self.running:
                self.display_status()

                # Press Q to exit (optional for visual interface)
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
        if not self.current_agent or time.time() - self.last_switch_time < self.help_cooldown:
            overlay = np.zeros((300, 600, 3), dtype=np.uint8)

            if self.current_agent:
                status_text = f"Active: {type(self.current_agent).__name__}"
                cv2.putText(overlay, status_text, (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            help_text = "Voice Commands:"
            cv2.putText(overlay, help_text, (50, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

            commands = [
                "'Object detection'",
                "'Scan barcode'",
                "'Read document'",
                "'Navigate'",
                "'Ecommerce'",
                "'Exit'"
            ]

            for i, cmd in enumerate(commands):
                cv2.putText(overlay, cmd, (50, 180 + i * 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

            cv2.imshow("VisionAI Control", overlay)

    def shutdown(self):
        speak("Shutting down all systems")
        self.running = False
        self.cleanup()

    def cleanup(self):
        for agent in self.agents.values():
            if hasattr(agent, 'terminate'):
                agent.terminate()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    master = MasterAgent()
    master.run()
