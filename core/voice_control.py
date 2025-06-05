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
            "navigate": "navigation",
            "navigation": "navigation",
            "find product": "ecommerce_agent",
            "search online": "ecommerce_agent",
            "ecommerce_agent": "ecommerce_agent",
            "exit": "exit"
        }

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)

            # Speak all command options (once per agent type)
            friendly_names = {
                "object_detection": "Object Detection",
                "barcode_scanner": "Barcode Scanner",
                "document_reader": "Document Reader",
                "navigation": "Navigation",
                "ecommerce_agent": "Search Online"
            }
            speak("Say a command: " + ", ".join(friendly_names.values()))

            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")

                for phrase, agent in self.command_map.items():
                    if phrase in text:
                        print(f"Command matched: {agent}")
                        return agent

                speak("Command not recognized. Please try again.")
                return None

            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Please try again.")
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that.")
            except sr.RequestError:
                speak("Speech service unavailable.")
            except Exception as e:
                print(f"Voice error: {e}")

            return None
