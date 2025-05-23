import sounddevice as sd
import numpy as np
import whisper
import tempfile
import os
import scipy.io.wavfile as wav
from core.utils import speak
from typing import Tuple, Optional
import logging


class DialogAgent:
    def __init__(self):
        # Initialize with better whisper model configuration
        self.model = whisper.load_model("small.en")  # Better accuracy for English
        self.sample_rate = 16000
        self.recording_duration = 7  # Increased from 5 seconds
        self.logger = logging.getLogger(__name__)

        # Configure location type synonyms
        self.location_keywords = {
            'hospital': ['hospital', 'clinic', 'medical center', 'doctor'],
            'school': ['school', 'college', 'university', 'academy'],
            'supermarket': ['supermarket', 'grocery', 'store', 'market'],
            'bus halt': ['bus stop', 'bus station', 'bus halt', 'transit']
        }

    def record_audio(self) -> str:
        """Record audio with better error handling and feedback"""
        try:
            speak("Where would you like to go? Examples: hospital, school, supermarket, or bus stop.")
            self.logger.info("Starting recording...")

            # Improved audio recording with device verification
            recording = sd.rec(
                int(self.recording_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                device=sd.default.device[0]  # Use default input device
            )
            sd.wait()
            self.logger.info("Recording completed")

            # Save to temp file with better cleanup handling
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                wav.write(temp_file.name, self.sample_rate, recording)
                return temp_file.name

        except Exception as e:
            self.logger.error(f"Recording failed: {e}")
            speak("Sorry, I couldn't record your voice. Please try again.")
            raise

    def _extract_location_type(self, text: str) -> Optional[str]:
        """Advanced location type extraction with synonym support"""
        text = text.lower().strip()
        self.logger.debug(f"Processing text: {text}")

        # First check for exact matches
        for loc_type, keywords in self.location_keywords.items():
            if any(f" {kw} " in f" {text} " for kw in keywords):
                return loc_type

        # Then check for partial matches
        for loc_type, keywords in self.location_keywords.items():
            if any(kw in text for kw in keywords):
                return loc_type

        return None

    def get_location_type(self) -> Optional[str]:
        """Get location type with better error recovery"""
        try:
            file_path = self.record_audio()
            result = self.model.transcribe(file_path)
            text = result["text"].strip()
            self.logger.info(f"Recognized speech: {text}")

            # Clean up temp file immediately
            try:
                os.unlink(file_path)
            except:
                pass

            loc_type = self._extract_location_type(text)

            if loc_type:
                speak(f"I heard: {text}. Looking for {loc_type}.")
                return loc_type
            else:
                speak(f"I heard: {text}, but didn't recognize a location type. Please try again.")
                return None

        except Exception as e:
            self.logger.error(f"Location type detection failed: {e}")
            speak("I couldn't understand the location. Please say something like 'hospital' or 'supermarket'.")
            return None

    def get_user_location(self) -> Tuple[Optional[float], Optional[float]]:
        """Get user location with better fallback options"""
        try:
            # Try GPS first (mock implementation - replace with real GPS)
            # lat, lon = self._get_gps_location()

            # Fallback to IP geolocation
            # lat, lon = self._get_ip_location()

            # Final fallback (should be replaced in production)
            self.logger.warning("Using default London coordinates")
            speak("Using default location in Central London for demonstration.")
            return (51.5074, -0.1278)  # Default: London

        except Exception as e:
            self.logger.error(f"Location detection failed: {e}")
            speak("Could not determine your location. Please enable location services.")
            return (None, None)

