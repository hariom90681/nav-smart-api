from fastapi import APIRouter
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import json

from app.route_details import get_all_stop_points
from app.mistral_client import mistral_client  # ✅ import Mistral client

# Initialize geocoder
geolocator = Nominatim(user_agent="navsmart")

# ------------------ ROUTE ROUTER ------------------
route_router = APIRouter(tags=["Route"])
itinerary_router = APIRouter(tags=["Itinerary"])

class MessageRequest(BaseModel):
    message: str

class ItineraryRequest(BaseModel):
    message: str


@route_router.post("/location/get-details-route")
async def get_details_route(req: MessageRequest):
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

    route_data = get_all_stop_points(
        start_location,
        end_location,
        "AIzaSyDDgJKSce1dwXMTZ886PDMqjaJrF9z1ErA"
    )

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
@itinerary_router.post("/location/get-itinerary")
async def get_itinerary(req: ItineraryRequest):
    prompt = f"""
    You are an expert travel planner AI.
    User message: "{req.message}"

    Generate a travel itinerary in valid JSON format:
    {{
      "reply": "<short friendly summary>",
      "itinerary": [
        {{
          "day": "Day 1",
          "location": "<city or area>",
          "activities": ["<activity1>", "<activity2>", ...]
        }}
      ]
    }}
    """

    try:
        # ✅ Call Mistral model
        response = mistral_client.text_generation(
            prompt,
            max_new_tokens=800,
            temperature=0.7,
            repetition_penalty=1.1,
        )

        # Clean and parse the output
        content = response.strip()
        content = content.replace("```json", "").replace("```", "").strip()

        itinerary_data = json.loads(content)
        return itinerary_data

    except json.JSONDecodeError:
        return {"error": "Model output was not valid JSON", "raw_output": content}
    except Exception as e:
        return {"error": f"Mistral API call failed: {str(e)}"}
