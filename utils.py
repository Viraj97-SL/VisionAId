import pygame
from gtts import gTTS
import tempfile
import os
import time
from threading import Lock
import cv2

pygame.mixer.init()


import tempfile
import os
from gtts import gTTS
import pygame
import time

def speak(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        filename = fp.name
        tts.save(filename)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    finally:
        try:
            pygame.mixer.quit()
            os.remove(filename)
        except Exception as e:
            print(f"Cleanup warning: {e}")



def get_camera():
    """Camera initialization helper"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Camera error")
    return cap
