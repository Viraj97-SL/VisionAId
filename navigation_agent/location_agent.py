import requests

class LocationAgent:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {"User-Agent": "VisionAID/1.0 (contact@example.com)"}  # Optional: contact info as per Nominatim policy

    def find_nearby(self, place_type, lat, lon):
        try:
            params = {
                "q": place_type,
                "format": "json",
                "limit": 1,
                "viewbox": f"{lon-0.01},{lat+0.01},{lon+0.01},{lat-0.01}",
                "bounded": 1
            }
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()  # Raises HTTPError if status is 4xx/5xx

            results = response.json()
            if results:
                return results[0]
        except requests.RequestException as e:
            print(f"[LocationAgent] Error: {e}")
        return None
