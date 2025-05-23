import time
from core.utils import speak

class Navigator:
    def __init__(self):
        pass

    def guide(self, directions):
        if not directions or len(directions) == 0:
            speak("No directions available.")
            return

        for i, step in enumerate(directions, start=1):
            speak(f"Step {i}: {step}")
            time.sleep(2)  # Small pause between instructions
