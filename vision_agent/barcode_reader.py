import cv2
from pyzbar import pyzbar
import requests
from core.utils import speak
import time
import warnings
import zmq
import json


class BarcodeReaderAgent:
    def __init__(self):
        self.running = True
        self.camera = cv2.VideoCapture(0)
        self.last_scanned = None
        self.scan_cooldown = 3
        self.min_confidence = 30

        # MCP Setup (non-blocking PUB)
        self.context = zmq.Context()
        self.mcp_socket = self.context.socket(zmq.PUB)
        self.mcp_socket.connect("tcp://localhost:5555")

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")

    def _publish_to_mcp(self, barcode_data, product_info):
        try:
            self.mcp_socket.send_json({
                "source": "vision",
                "agent": "barcode",
                "data": {
                    "code": barcode_data,
                    "product": product_info[0] if product_info else None,
                    "brand": product_info[1] if product_info else None,
                },
                "timestamp": time.time()
            })
        except Exception as e:
            print(f"[MCP ERROR] Failed to publish: {e}")

    def run(self):
        try:
            warnings.filterwarnings("ignore", category=RuntimeWarning)

            test_ret, test_frame = self.camera.read()
            if not test_ret:
                speak("Camera failed to initialize")
                return

            cv2.imshow("Camera Test", test_frame)
            cv2.waitKey(1000)
            cv2.destroyWindow("Camera Test")

            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    speak("Camera error occurred")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                barcodes = pyzbar.decode(gray, symbols=[
                    pyzbar.ZBarSymbol.QRCODE,
                    pyzbar.ZBarSymbol.EAN13,
                    pyzbar.ZBarSymbol.CODE128
                ])

                for barcode in barcodes:
                    try:
                        barcode_data = barcode.data.decode('utf-8')
                        current_time = time.time()

                        if (barcode_data != self.last_scanned or
                                (current_time - getattr(self, 'last_scanned_time', 0)) > self.scan_cooldown):
                            product_info = self.lookup_product(barcode_data)
                            feedback = self.format_feedback(barcode_data, product_info)

                            # MCP publishing
                            self._publish_to_mcp(barcode_data, product_info)

                            # Drawing rectangle
                            x, y, w, h = barcode.rect
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)

                            (tw, th), _ = cv2.getTextSize(feedback[:50], cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                            cv2.rectangle(frame, (x, y - th - 10), (x + tw, y), (0, 255, 0), -1)
                            cv2.putText(frame, feedback[:50], (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                            speak(feedback)
                            self.last_scanned = barcode_data
                            self.last_scanned_time = current_time

                    except Exception as e:
                        print(f"Barcode error: {e}")
                        continue

                # UI
                cv2.putText(frame, "Scan a barcode/QR code", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, "Press 'q' to quit", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                cv2.imshow("Barcode Scanner", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            speak(f"Scanning error: {str(e)}")
        finally:
            self.terminate()
            warnings.resetwarnings()

    def format_feedback(self, code, product_info):
        if product_info:
            name, brand, quantity, ingredients = product_info
            return f"{brand} {name}, {quantity}. Ingredients: {ingredients[:100]}..."
        return f"Unknown product (Code: {code})"

    def lookup_product(self, barcode):
        try:
            response = requests.get(
                f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 1:
                    product = data['product']
                    return (
                        product.get('product_name', "Unknown"),
                        product.get('brands', "Unknown"),
                        product.get('quantity', ""),
                        product.get('ingredients_text', "No ingredients")
                    )
        except requests.RequestException as e:
            print(f"[LOOKUP ERROR] {e}")
        return None

    def terminate(self):
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        if hasattr(self, 'mcp_socket'):
            self.mcp_socket.close()
        if hasattr(self, 'context'):
            self.context.term()


if __name__ == "__main__":
    agent = BarcodeReaderAgent()
    agent.run()
