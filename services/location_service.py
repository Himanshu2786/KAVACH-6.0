"""
KAVACH 6.0 - Real Geolocation Detection Service.
Adheres strictly to KAVACH Privacy and Transparency rules:
- NEVER invents fake/demo locations
- Queries real approximate network geolocation when GPS unavailable
- Distinguishes DEVICE_LOCATION vs APPROXIMATE_NETWORK_LOCATION
"""

from typing import Dict, Any, Optional
import httpx

class LocationService:
    def __init__(self):
        self._cached_location: Optional[Dict[str, Any]] = None

    def get_current_location(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Retrieves real geographic coordinates.
        Never invents coordinates. Returns status LOCATION_UNAVAILABLE on failure.
        """
        if self._cached_location and not force_refresh:
            return self._cached_location

        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get("https://ipapi.co/json/")
                if resp.status_code == 200:
                    data = resp.json()
                    lat = data.get("latitude")
                    lon = data.get("longitude")
                    if lat is not None and lon is not None:
                        loc = {
                            "success": True,
                            "status": "APPROXIMATE_NETWORK_LOCATION",
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "country": data.get("country_name", "Unknown"),
                            "city": data.get("city", "Unknown"),
                            "is_approximate": True
                        }
                        self._cached_location = loc
                        return loc
        except Exception:
            pass

        return {
            "success": False,
            "status": "LOCATION_UNAVAILABLE",
            "latitude": None,
            "longitude": None,
            "country": None,
            "city": None,
            "is_approximate": False
        }

location_service = LocationService()
