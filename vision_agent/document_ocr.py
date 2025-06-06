import cv2
import pytesseract
from core.utils import speak
import numpy as np
import zmq
import time
from core.mcp_logger import MCPLogger



class DocumentOCRAgent:
    def __init__(self):
        self.running = True
        self.camera = cv2.VideoCapture(0)

        # MCP Setup (ZeroMQ Publisher)
        self.context = zmq.Context()
        self.mcp_socket = self.context.socket(zmq.PUB)
        self.mcp_socket.connect("tcp://localhost:5555")  # Connect to MCP
        self.logger = MCPLogger()

        # Tesseract path (update if needed)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")

    def _publish_to_mcp(self, text):
        """Send OCR results to MCP and SQLite"""
        message = {
            "source": "vision",
            "agent": "document",
            "data": {
                "text": text[:1000],
                "char_count": len(text)
            },
            "timestamp": time.time()
        }

        # Send to MCP (ZeroMQ)
        self.mcp_socket.send_json(message)

        # Also log into SQLite
        self.logger.insert_message(message)

    def run(self):
        """Main execution loop called by master agent"""
        try:
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    speak("Failed to capture frame")
                    break

                self._display_ui(frame)
                key = cv2.waitKey(1)

                if key == ord('s'):  # Scan command
                    self._process_document(frame)
                elif key == ord('q'):  # Quit command
                    break

        except Exception as e:
            speak(f"Document scanning error: {str(e)}")
        finally:
            self.terminate()

    def _display_ui(self, frame):
        """Show instructions and camera feed"""
        cv2.putText(frame, "Press 's' to scan document", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow("Document Scanner", frame)

    def _process_document(self, frame):
        """Handle OCR processing and MCP publishing"""

        # Optional: crop document region if detected
        region = self._detect_document_region(frame)
        if region:
            x, y, w, h = region
            frame = frame[y:y + h, x:x + w]

        processed_image = self._preprocess_image(frame)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_image, config=custom_config)

        if text.strip():
            self._publish_to_mcp(text)
            speak("I found some text. Here's what I see:")
            print("Extracted Text:", text)
            speak(text[:300])
        else:
            speak("No text detected in the document")

    def _preprocess_image(self, img):
        """Enhanced image preprocessing for OCR"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255,
                                       cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 4)
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        resized = cv2.resize(morph, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        return resized

    def _detect_document_region(self, frame):
        """Attempt to detect the document boundary"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(gray, 75, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                return cv2.boundingRect(approx)
        return None

    def terminate(self):
        """Cleanup for master agent"""
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        self.context.destroy()
        self.logger.close()


if __name__ == "__main__":
    agent = DocumentOCRAgent()
    agent.run()
