from fastapi import APIRouter
from pydantic import BaseModel
from geopy.geocoders import Nominatim
from openai import OpenAI
import json

from app.route_details import get_all_stop_points

# Initialize geocoder and OpenAI
geolocator = Nominatim(user_agent="navsmart")
client = OpenAI(api_key="https://maps.googleapis.com/maps/api/js?key=AIzaSyDDgJKSce1dwXMTZ886PDMqjaJrF9z1ErA&callback=initMap")  # Replace with actual key

# ------------------ ROUTE ROUTER ------------------
route_router = APIRouter(tags=["Route"])

class MessageRequest(BaseModel):
    message: str

@route_router.post("/location/get-details-route")
async def get_details_route(req: MessageRequest):
    message = req.message.lower()

    # Extract start and end
    if "from" in message and "to" in message:
        parts = message.split("from")[1].split("to")
        start_location = parts[0].strip()
        end_location = parts[1].strip()
    else:
        return {
            "reply": "Sorry, I couldn't understand the route request.",
            "start": {"error": "Missing 'from' location"},
            "end": {"error": "Missing 'to' location"}
        }

    # Geocode both locations

    # ✅ Fetch all stop points between start and end
    route_data = get_all_stop_points(
        start_location,
        end_location,
        "AIzaSyDDgJKSce1dwXMTZ886PDMqjaJrF9z1ErA"
    )

    # ✅ Success Response
    return route_data

@route_router.post("/location/get-route")
async def get_route(req: MessageRequest):
    message = req.message.lower()

    if "from" in message and "to" in message:
        parts = message.split("from")[1].split("to")
        start_location = parts[0].strip()
        end_location = parts[1].strip()
    else:
        return {
            "reply": "Sorry, I couldn't understand the route request.",
            "start": {"error": "Missing 'from' location"},
            "end": {"error": "Missing 'to' location"}
        }

    start = geolocator.geocode(start_location)
    end = geolocator.geocode(end_location)

    if not start or not end:
        return {
            "reply": "Sorry, I couldn't find one of the locations.",
            "start": {"error": "Invalid start location"} if not start else {},
            "end": {"error": "Invalid end location"} if not end else {}
        }

    return {
        "reply": f"Here's the best route from {start_location} to {end_location}.",
        "start": {"latitude": start.latitude, "longitude": start.longitude},
        "end": {"latitude": end.latitude, "longitude": end.longitude}
    }

# ------------------ ITINERARY ROUTER ------------------
itinerary_router = APIRouter(tags=["Itinerary"])

class ItineraryRequest(BaseModel):
    message: str


@itinerary_router.post("/location/get-itinerary")
async def get_itinerary(req: ItineraryRequest):
    prompt = f"""
    User message: "{req.message}"
    Generate a travel itinerary in JSON format with:
    - reply: a short summary message
    - itinerary: a list of days, each with:
      - day
      - location
      - activities (list of strings)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content
        try:
            itinerary_data = json.loads(content)
            return itinerary_data
        except Exception as e:
            return {"error": f"Failed to parse itinerary: {str(e)}"}

    except Exception as e:
        return {"error": f"OpenAI API call failed: {str(e)}"}
