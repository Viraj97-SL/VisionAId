import threading
import zmq
import cv2
import torch
from PIL import Image
import time
import pyttsx3  # For text-to-speech
from transformers import AutoModelForImageClassification, AutoImageProcessor


class EmotionDetectionAgent:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.running = False
        self.last_spoken_emotion = None
        self.last_spoken_time = 0
        self.speech_cooldown = 3  # seconds between speech outputs

        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Slower speech rate

        # Load emotion detection model
        self.model = AutoModelForImageClassification.from_pretrained(
            "dima806/facial_emotions_image_detection"
        ).to(self.device)
        self.processor = AutoImageProcessor.from_pretrained(
            "dima806/facial_emotions_image_detection"
        )

        # Emotion labels
        self.emotion_labels = {
            0: "angry",
            1: "disgust",
            2: "fear",
            3: "happy",
            4: "neutral",
            5: "sad",
            6: "surprise"
        }

        # OpenCV face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def speak_emotion(self, emotion):
        current_time = time.time()
        if (emotion != self.last_spoken_emotion or
                current_time - self.last_spoken_time > self.speech_cooldown):
            self.tts_engine.say(f"I see you look {emotion}")
            self.tts_engine.runAndWait()
            self.last_spoken_emotion = emotion
            self.last_spoken_time = current_time

    def detect_emotion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return []

        x, y, w, h = faces[0]
        face_roi = frame[y:y + h, x:x + w]
        image = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        top_probs, top_labels = torch.topk(probs, k=3)

        return [{
            "label": self.emotion_labels[int(top_labels[0][i])],
            "score": float(top_probs[0][i]),
            "bbox": (x, y, w, h)
        } for i in range(top_probs.shape[1])]

    def run(self):
        context = zmq.Context()
        publisher = context.socket(zmq.PUB)
        publisher.connect("tcp://localhost:5555")

        cap = cv2.VideoCapture(0)
        self.running = True

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break

                emotions = self.detect_emotion(frame)
                if emotions:
                    top_emotion = emotions[0]

                    # Publish to ZMQ
                    publisher.send_json({
                        "agent": "emotion",
                        "data": {
                            "top_emotion": top_emotion["label"],
                            "confidence": top_emotion["score"]
                        },
                        "timestamp": time.time()
                    })

                    # Speak the emotion
                    if top_emotion["score"] > 0.7:  # Only speak if confidence > 70%
                        self.speak_emotion(top_emotion["label"])

                    # Visual feedback
                    x, y, w, h = top_emotion["bbox"]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame,
                                f"{top_emotion['label']} ({top_emotion['score']:.2f})",
                                (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 255, 0),
                                2)

                cv2.imshow("Emotion Detection", frame)

                # Check for 'q' key press
                key = cv2.waitKey(1)
                if key == ord('q') or key == 27:  # 'q' or ESC
                    self.running = False
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.tts_engine.stop()
            publisher.close()
            context.term()

    def run_non_blocking(self):
        """Run emotion detection in a background thread."""
        if not self.running:
            self.running = True
            threading.Thread(target=self.run, daemon=True).start()

    def terminate(self):
        """Stop the emotion detection agent."""
        self.running = False


if __name__ == "__main__":
    agent = EmotionDetectionAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
    finally:
        agent.terminate()
