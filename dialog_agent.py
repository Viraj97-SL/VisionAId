import speech_recognition as sr
from core.utils import speak

class DialogAgent:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def get_location_type(self):
        speak("Where do you want to go? You can say hospital, supermarket, school or bus halt.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                response = self.recognizer.recognize_google(audio).lower().strip()
                print(f"Heard: {response}")

                # Normalize known types
                valid_types = {
                    "hospital": "hospital",
                    "supermarket": "supermarket",
                    "school": "school",
                    "bus halt": "bus stop",
                    "bus stop": "bus stop",
                }

                for key in valid_types:
                    if key in response:
                        return valid_types[key]

                speak("Sorry, I only support hospital, supermarket, school, or bus stop.")
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Please try again.")
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand. Please try again.")
            except sr.RequestError as e:
                speak(f"Speech recognition error: {str(e)}")

        return None

    def get_user_location(self):
        # Dummy coordinates for testing (e.g., Central London)
        # Replace with real GPS if available or ask user input later
        return 51.5074, -0.1278  # Latitude, Longitude
