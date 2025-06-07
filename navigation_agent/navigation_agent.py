from agents.navigation.dialog_agent import DialogAgent
from agents.navigation.location_agent import LocationAgent
from agents.navigation.route_planner import RoutePlanner
from agents.navigation.navigator import Navigator
from core.utils import speak
import logging


class NavigationAgent:
    def __init__(self):
        self.dialog = DialogAgent()
        self.locator = LocationAgent()
        self.router = RoutePlanner()
        self.navigator = Navigator()
        self.logger = logging.getLogger(__name__)

        # Configure valid location types and their synonyms
        self.valid_types = {
            "hospital": ["hospital", "clinic", "medical center"],
            "supermarket": ["supermarket", "grocery", "store", "market"],
            "school": ["school", "college", "university"],
            "bus halt": ["bus stop", "bus station", "bus halt", "transit"]
        }

    def _normalize_location_type(self, user_input: str) -> str:
        """Match user input to valid location type using synonyms."""
        user_input = user_input.lower().strip()
        for main_type, synonyms in self.valid_types.items():
            if user_input in synonyms:
                return main_type
        return user_input  # Return original if no match found

    def run(self):
        """Main navigation workflow with enhanced error handling."""
        speak("Navigation assistant activated. Where would you like to go?")

        try:
            # Step 1: Get destination type
            place_type = self.dialog.get_location_type()
            if not place_type:
                speak("Please specify a destination type like hospital, supermarket, or bus stop.")
                return

            # Normalize and validate location type
            place_type = self._normalize_location_type(place_type)
            if place_type not in self.valid_types:
                speak(f"Sorry, I don't support navigation to {place_type}. "
                      f"Please try: hospital, supermarket, school, or bus stop.")
                return

            # Step 2: Get current location
            speak("Getting your current location...")
            lat, lon = self.dialog.get_user_location()
            if None in (lat, lon):
                speak("Unable to determine your location. Please ensure location services are enabled.")
                return

            # Step 3: Find nearby destinations
            speak(f"Searching for nearby {place_type}s...")
            destination = self.locator.find_nearby(place_type, lat, lon)
            if not destination:
                speak(f"Couldn't find any {place_type} near your location. "
                      "Try a different location type or broader area.")
                return

            # Step 4: Process destination
            speak(f"Found {destination.get('display_name', 'a location')}. "
                  "Calculating the best route...")
            try:
                end_lat = float(destination["lat"])
                end_lon = float(destination["lon"])
            except (KeyError, ValueError) as e:
                self.logger.error(f"Destination coordinate error: {e}")
                speak("Error processing the destination coordinates.")
                return

            # Step 5: Get directions
            directions = self.router.get_directions(lat, lon, end_lat, end_lon)
            if any("error" in d.lower() or "fail" in d.lower() for d in directions):
                speak("Unable to calculate the route. The destination might be too far or inaccessible by foot.")
                self.logger.error(f"Routing failed. Response: {directions}")
                return

            # Step 6: Begin navigation
            speak(f"Route found with {len(directions)} steps. Beginning navigation now.")
            try:
                self.navigator.guide(directions)
            except Exception as e:
                self.logger.error(f"Navigation failed: {e}")
                speak("Navigation system encountered an error. Please try again.")
                return

            speak("You have arrived at your destination. Navigation complete.")

        except Exception as e:
            self.logger.exception("Critical navigation error")
            speak("A serious error occurred in the navigation system. Restarting...")
            raise  # Re-raise for upstream handling

    def terminate(self):
        """Clean up resources and stop navigation."""
        try:
            self.navigator.stop_guidance()
            speak("Navigation stopped")
        except Exception as e:
            self.logger.error(f"Error during termination: {e}")
            speak("Error while stopping navigation.")
