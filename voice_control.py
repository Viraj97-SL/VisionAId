
import speech_recognition as sr
from core.utils import speak


class VoiceControl:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.command_map = {
            "object detection": "object_detection",
            "detect objects": "object_detection",
            "barcode": "barcode_scanner",
            "scan code": "barcode_scanner",
            "document": "document_reader",
            "read text": "document_reader",
            "exit": "exit"
        }

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            speak("Say a command: Object Detection, Barcode Scanner, or Document Reader")

            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")

                for phrase, agent in self.command_map.items():
                    if phrase in text:
                        return agent

                return None

            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that.")
            except sr.RequestError:
                speak("Speech service unavailable.")
            except Exception as e:
                print(f"Voice error: {e}")
            return None
