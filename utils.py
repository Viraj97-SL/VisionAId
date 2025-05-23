import pygame
from gtts import gTTS
import tempfile
import os
import time
from threading import Lock
import cv2

pygame.mixer.init()


def speak(text):
    """Reliable audio playback with guaranteed file availability"""
    try:
        # Create persistent temp file (not auto-deleted)
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_path = temp_file.name
        temp_file.close()  # Close immediately after creation

        # Generate and save speech
        tts = gTTS(text=text, lang='en')
        tts.save(temp_path)

        # Load and play
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    except Exception as e:
        print(f"Audio generation/playback error: {e}")
    finally:
        # Cleanup after playback finishes
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"Cleanup warning: {e}")  # Non-critical error


def get_camera():
    """Camera initialization helper"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Camera error")
    return cap