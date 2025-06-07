import time
from core.utils import speak

class Navigator:
    def __init__(self):
        self.active = False  # optional tracking flag

    def guide(self, directions):
        if not directions or len(directions) == 0:
            speak("No directions available.")
            return

        self.active = True
        for i, step in enumerate(directions, start=1):
            if not self.active:
                speak("Navigation stopped.")
                return
            speak(f"Step {i}: {step}")
            time.sleep(2)

    def stop_guidance(self):
        """Stop the current guidance session"""
        self.active = False
