import sounddevice as sd
import numpy as np
import whisper
import tempfile
import os
import scipy.io.wavfile as wav
from core.utils import speak



class DialogAgent:
    def __init__(self):
        self.model = whisper.load_model("base")  # You can use "tiny", "small", etc.

    def record_audio(self, duration=5, fs=16000):
        speak("Where do you want to go? Say something like 'nearby hospital', 'school', 'supermarket', or 'bus halt'.")
        print("Recording...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        print("Recording finished.")

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(temp_file.name, fs, recording)
        return temp_file.name

    def get_location_type(self):
        try:
            file_path = self.record_audio()
            result = self.model.transcribe(file_path)
            text = result["text"].lower().strip()
            print(f"Whisper Transcription: {text}")

            # Check if known location type is mentioned
            for keyword in ["hospital", "school", "supermarket", "bus halt"]:
                if keyword in text:
                    return keyword

            speak("I couldn't understand the location type. Please try again.")
            return None

        except Exception as e:
            print(f"[DialogAgent Error] {e}")
            speak("An error occurred while processing your voice.")
            return None

    def get_user_location(self):
        # TEMPORARY: Replace with your own GPS or IP-based method
        return (51.5074, -0.1278)  # Central London example
