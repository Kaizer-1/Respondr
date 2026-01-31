import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def geocode_location(location_text: str):
    """
    Converts text location into lat/lng using Google Maps
    """
    if not location_text or not GOOGLE_API_KEY:
        return None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_text,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params, timeout=5)
    data = response.json()

    if data.get("status") != "OK":
        return None

    result = data["results"][0]

    return {
        "formatted_address": result["formatted_address"],
        "lat": result["geometry"]["location"]["lat"],
        "lng": result["geometry"]["location"]["lng"],
        "place_id": result["place_id"],
        "confidence": 0.9
    }