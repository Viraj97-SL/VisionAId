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
        lat, lon = self.dialog.get_user_location()

        destination = self.locator.find_nearby(place_type, lat, lon)
        if not destination:
            speak(f"Sorry, no {place_type} found nearby.")
            return

        speak(f"Found a {place_type} at {destination['display_name']}. Planning route...")
        end_lat = float(destination["lat"])
        end_lon = float(destination["lon"])

        directions = self.router.get_directions(lat, lon, end_lat, end_lon)
        speak("Starting navigation.")
        self.navigator.guide(directions)

    def terminate(self):
        speak("Navigation agent stopped.")