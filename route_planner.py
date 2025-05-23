import requests
from typing import List, Optional, Tuple
import logging


class RoutePlanner:
    """Handles route planning using OSRM API with comprehensive error handling."""

    def __init__(self):
        self.base_url = "http://router.project-osrm.org/route/v1/foot/"
        self.alternate_services = [
            "https://routing.openstreetmap.de/routed-foot/route/v1/driving/"
        ]
        self.current_service = 0
        self.timeout = 15
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _make_request(self, coordinates: str, params: dict) -> Optional[dict]:
        """Try multiple services until a successful response is received."""
        services = [self.base_url] + self.alternate_services

        for service in services:
            try:
                url = f"{service}{coordinates}"
                self.logger.debug(f"Attempting request to: {url}")

                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Service {service} failed: {str(e)}")
                continue

        return None

    def _parse_directions(self, data: dict) -> List[str]:
        """Safely extract directions from API response with multiple fallbacks."""
        directions = []

        try:
            route = data["routes"][0]
            legs = route["legs"]

            for leg in legs:
                for step in leg["steps"]:
                    # Primary method: maneuver instruction
                    if "maneuver" in step:
                        maneuver = step["maneuver"]
                        if "instruction" in maneuver:
                            directions.append(maneuver["instruction"])
                            continue

                    # Fallback 1: Road name + maneuver type
                    if "name" in step and step["name"]:
                        road_name = step["name"]
                        if "maneuver" in step and "type" in step["maneuver"]:
                            maneuver_type = step["maneuver"]["type"]
                            directions.append(
                                f"{maneuver_type.capitalize()} onto {road_name}"
                            )
                            continue
                        directions.append(f"Continue on {road_name}")
                        continue

                    # Fallback 2: Distance/duration info
                    if "distance" in step and "duration" in step:
                        dist = max(1, round(step["distance"] / 1000, 1))
                        directions.append(
                            f"Proceed for {dist} km ({step['duration']} secs)"
                        )
                        continue

                    # Final fallback
                    directions.append("Proceed to next waypoint")

        except (KeyError, IndexError, TypeError) as e:
            self.logger.error(f"Parse error: {str(e)}")
            return ["Received incomplete route data"]

        return directions if directions else ["No turn-by-turn instructions available"]

    def get_directions(
            self,
            start_lat: float,
            start_lon: float,
            end_lat: float,
            end_lon: float
    ) -> List[str]:
        """
        Get walking directions between two points.

        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Destination latitude
            end_lon: Destination longitude

        Returns:
            List of direction strings or error messages
        """
        # Validate coordinates
        try:
            coords = (
                float(start_lon), float(start_lat),
                float(end_lon), float(end_lat)
            )
            if not all(-180 <= lon <= 180 for lon in [coords[0], coords[2]]):
                raise ValueError("Longitude out of range")
            if not all(-90 <= lat <= 90 for lat in [coords[1], coords[3]]):
                raise ValueError("Latitude out of range")

            coordinates = f"{coords[0]},{coords[1]};{coords[2]},{coords[3]}"
        except (ValueError, TypeError) as e:
            self.logger.error(f"Invalid coordinates: {str(e)}")
            return [f"Invalid coordinates: {str(e)}"]

        # API parameters
        params = {
            "overview": "false",
            "steps": "true",
            "alternatives": "false",
            "geometries": "geojson"
        }

        # Get route data
        data = self._make_request(coordinates, params)
        if not data:
            return ["All routing services failed. Please try again later."]

        # Check for API errors
        if data.get("code") != "Ok":
            msg = data.get("message", "Unknown routing error")
            self.logger.error(f"API error: {msg}")
            return [f"Routing error: {msg}"]

        return self._parse_directions(data)

    @staticmethod
    def format_debug_response(data: dict) -> str:
        """Create human-readable debug output of API response."""
        debug_info = []

        try:
            # Basic route info
            if "routes" in data and data["routes"]:
                route = data["routes"][0]
                debug_info.append(
                    f"Route distance: {route.get('distance', '?')}m | "
                    f"Duration: {route.get('duration', '?')}s"
                )

                # Waypoints info
                if "waypoints" in data:
                    debug_info.append(
                        f"Waypoints: {len(data['waypoints'])} points"
                    )

                # Legs and steps
                if "legs" in route and route["legs"]:
                    for i, leg in enumerate(route["legs"], 1):
                        debug_info.append(
                            f"\nLeg {i}: {len(leg.get('steps', []))} steps"
                        )
                        for j, step in enumerate(leg.get("steps", []), 1):
                            step_info = [
                                f"Step {j}:",
                                step.get("maneuver", {}).get("type", "?"),
                                step.get("name", "unnamed road"),
                                f"{step.get('distance', '?')}m"
                            ]
                            debug_info.append(" | ".join(step_info))

        except Exception as e:
            debug_info.append(f"Debug formatting failed: {str(e)}")

        return "\n".join(debug_info)
