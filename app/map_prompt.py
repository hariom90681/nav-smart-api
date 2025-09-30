import re
import ssl

from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim
from transformers import pipeline
import certifi

# Load NER model once
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)


ctx = ssl.create_default_context(cafile=certifi.where())
# ctx = ssl.create_default_context()
# ctx.check_hostname = False
# ctx.verify_mode = ssl.CERT_NONE
geolocator = Nominatim(user_agent="geoapi", ssl_context=ctx)


def extract_locations(text: str):
    """Extract location names from free text using NER."""
    entities = ner_pipeline(text)
    locations = [ent["word"] for ent in entities if ent["entity_group"] in ["LOC", "ORG", "PER", "MISC", "GPE"]]
    return locations
#
#
# def get_coordinates(place: str):
#     try:
#         loc = geolocator.geocode(place)
#         if loc:
#             return {"name": place, "latitude": loc.latitude, "longitude": loc.longitude}
#         return {"name": place, "error": "Not found"}
#     except GeocoderUnavailable:
#         return {"name": place, "error": "Geocoding service unavailable"}


def get_route_from_text(text: str) -> dict:
    """
    Extracts start and end destinations from human-like language
    and returns their geo-coordinates.
    """
    locations = extract_locations(text)

    if len(locations) < 2:
        return {"error": "Could not detect both start and end locations"}

    start = get_coordinates(locations[0])
    end = get_coordinates(locations[1])

    return {"start": start, "end": end}


# def extract_locations(text: str):
#     """
#     Extract start and end locations from natural sentences like:
#     - "from Delhi to Kolkata"
#     - "go to Paris from Berlin"
#     """
#
#     # Try pattern: "from X to Y"
#     match = re.search(r"from (.+?) to (.+)", text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip(), match.group(2).strip()
#
#     # Try pattern: "to X from Y"
#     match = re.search(r"to (.+?) from (.+)", text, re.IGNORECASE)
#     if match:
#         return match.group(2).strip(), match.group(1).strip()
#
#     return None, None


def get_coordinates(place: str):
    """
    Get latitude/longitude for a place using Nominatim.
    """
    try:
        loc = geolocator.geocode(place, timeout=10)
        if loc:
            return {"name": place, "latitude": loc.latitude, "longitude": loc.longitude}
        else:
            return {"name": place, "error": "Not found"}
    except GeocoderUnavailable:
        return {"name": place, "error": "Geocoding service unavailable"}
    except Exception as e:
        return {"name": place, "error": str(e)}
