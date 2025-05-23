import requests

class RoutePlanner:
    def __init__(self):
        self.base_url = "http://router.project-osrm.org/route/v1/foot/"

    def get_directions(self, start_lat, start_lon, end_lat, end_lon):
        coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            "overview": "false",
            "steps": "true"
        }

        try:
            response = requests.get(self.base_url + coordinates, params=params, timeout=5)
            response.raise_for_status()  # Handle HTTP errors

            data = response.json()
            if data.get("routes"):
                steps = data["routes"][0]["legs"][0]["steps"]
                directions = [step["maneuver"]["instruction"] for step in steps if "maneuver" in step]
                return directions

        except requests.RequestException as e:
            print(f"[RoutePlanner] Error fetching directions: {e}")

        return ["Sorry, route could not be found."]
