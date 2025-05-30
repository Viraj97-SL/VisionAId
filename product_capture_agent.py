import sounddevice as sd
import whisper
import tempfile
import scipy.io.wavfile as wav
import os
from core.utils import speak
import logging

class ProductCaptureAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = whisper.load_model("small.en")
        self.sample_rate = 16000
        self.duration = 7
        self.product_categories = {
            'electronics': ['phone', 'laptop', 'tablet', 'camera', 'headphones'],
            'clothing': ['shirt', 'pants', 'dress', 'shoes', 'jacket'],
            'books': ['book', 'novel', 'textbook', 'magazine'],
            'home': ['furniture', 'appliance', 'decoration', 'utensil']
        }

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
            print ("Recording error. Try again.")
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

    def get_product_name(self):
        file_path = self.record_audio("What product are you looking for today?")
        if not file_path:
            return None
        text = self.transcribe_audio(file_path)
        if not text:
            return None
        for category, keywords in self.product_categories.items():
            if any(f" {kw} " in f" {text} " for kw in keywords):
                speak(f"Heard: {text}. Searching {category}.")
                print (f"Heard: {text}. Searching {category}.")
                return text
        speak(f"Heard: {text}. Searching.")
        print (f"Heard: {text}. Searching.")
        return text
