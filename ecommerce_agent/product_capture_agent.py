import sounddevice as sd
import whisper
import tempfile
import scipy.io.wavfile as wav
import os
import logging
from core.utils import speak
from transformers import pipeline

class ProductCaptureAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = whisper.load_model("small.en")
        self.sample_rate = 16000
        self.duration = 7

        # 🧠 Add HuggingFace Zero-Shot Classifier
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.categories = ["electronics", "clothing", "books", "home", "groceries", "beauty", "sports"]

    def record_audio(self, prompt):
        try:
            speak(prompt)
            recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                wav.write(temp_file.name, self.sample_rate, recording)
                return temp_file.name
        except Exception as e:
            self.logger.error(f"Recording failed: {e}")
            speak("Recording error. Try again.")
            print("Recording error. Try again.")
            return None

    def transcribe_audio(self, file_path):
        try:
            result = self.model.transcribe(file_path)
            return result["text"].strip().lower()
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            speak("Transcription error.")
            return None
        finally:
            try:
                os.unlink(file_path)
            except:
                pass

    def classify_category(self, text):
        try:
            result = self.classifier(text, self.categories)
            top_category = result['labels'][0]  # Highest confidence
            score = result['scores'][0]
            return top_category, score
        except Exception as e:
            self.logger.error(f"Classification error: {e}")
            return "general", 0.0

    def get_product_name(self):
        file_path = self.record_audio("What product are you looking for today?")
        if not file_path:
            return None
        text = self.transcribe_audio(file_path)
        if not text:
            return None

        category, confidence = self.classify_category(text)
        speak(f"Heard: {text}. Searching {category}.")
        print(f"Heard: {text}. Category: {category} (Confidence: {confidence:.2f})")

        return text  # You can return `text, category` if you want category info too
