import cv2
import pytesseract
from core.utils import speak
import numpy as np


class DocumentOCRAgent:
    def __init__(self):
        self.running = True
        self.camera = cv2.VideoCapture(0)

        # Update this path if needed
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")

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
        """Handle OCR processing"""
        processed_image = self._preprocess_image(frame)
        text = pytesseract.image_to_string(processed_image)

        if text.strip():
            speak("I found some text. Here's what I see:")
            print("Extracted Text:", text)
            speak(text[:300])  # Limit audio output
        else:
            speak("No text detected in the document")

    def _preprocess_image(self, img):
        """Enhance image for better OCR"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.adaptiveThreshold(gray, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((1, 1), np.uint8)
        return cv2.dilate(processed, kernel, iterations=1)

    def terminate(self):
        """Cleanup for master agent"""
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # For standalone testing
    agent = DocumentOCRAgent()
    agent.run()

