from agents.navigation.dialog_agent import DialogAgent
from agents.navigation.location_agent import LocationAgent
from agents.navigation.route_planner import RoutePlanner
from agents.navigation.navigator import Navigator
from core.utils import speak

class NavigationAgent:
    def __init__(self):
        self.dialog = DialogAgent()
        self.locator = LocationAgent()
        self.router = RoutePlanner()
        self.navigator = Navigator()

    def run(self):
        speak("Navigation agent activated.")

        place_type = self.dialog.get_location_type()
        if not place_type:
            speak("I didn't catch that. Please say a location type like hospital, supermarket, school, or bus halt.")
            return

        valid_types = ["hospital", "supermarket", "school", "bus halt"]
        if place_type not in valid_types:
            speak(f"'{place_type}' is not a valid option.")
            return

        # ✅ You must define your current location manually or via GPS in get_user_location
        lat, lon = self.dialog.get_user_location()
        if lat is None or lon is None:
            speak("Could not determine your current location.")
            return

        destination = self.locator.find_nearby(place_type, lat, lon)
        if not destination:
            speak(f"Sorry, no {place_type} found nearby.")
            return

        speak(f"Found a {place_type} at {destination['display_name']}. Planning route...")
        end_lat = float(destination["lat"])
        end_lon = float(destination["lon"])

        directions = self.router.get_directions(lat, lon, end_lat, end_lon)
        if not directions or directions == ["Route could not be found"]:
            speak("I couldn't find a walking route to that location.")
            return

        speak("Starting navigation.")
        self.navigator.guide(directions)

    def terminate(self):
        speak("Navigation agent stopped.")
