from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import json

from app.route_details import get_all_stop_points
import httpx

# Initialize geocoder
geolocator = Nominatim(user_agent="navsmart")
import os
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

route_router = APIRouter(tags=["Route"])
itinerary_router = APIRouter(tags=["Itinerary"])
chat_router = APIRouter(tags=["Chat"])

class MessageRequest(BaseModel):
    message: str

class ItineraryRequest(BaseModel):
    message: str


@route_router.post("/location/get-details-route")
async def get_details_route(req: MessageRequest):
    message = req.message.lower().strip()

    if "from" in message and "to" in message:
        try:
            after_from = message.split("from", 1)[1]
            parts = after_from.split("to", 1)
            start_location = parts[0].strip()
            end_location = parts[1].strip()
        except IndexError:
            return {
                "reply": "Sorry, I couldn't parse your route request properly.",
                "start": {"error": "Missing start location"},
                "end": {"error": "Missing end location"}
            }
    else:
        return {
            "reply": "Sorry, I couldn't understand the route request. Please include 'from' and 'to'.",
            "start": {"error": "Missing 'from'"},
            "end": {"error": "Missing 'to'"}
        }

    route_data = get_all_stop_points(
        start_location,
        end_location,
        "AIzaSyDDgJKSce1dwXMTZ886PDMqjaJrF9z1ErA"  # Your Google Maps API key
    )

    return route_data


@route_router.post("/location/get-route")
async def get_route(req: MessageRequest):
    message = req.message.lower().strip()

    if "from" in message and "to" in message:
        try:
            after_from = message.split("from", 1)[1]
            parts = after_from.split("to", 1)
            start_location = parts[0].strip()
            end_location = parts[1].strip()
        except IndexError:
            return {
                "reply": "Sorry, I couldn't parse your route request properly.",
                "start": {"error": "Missing start location"},
                "end": {"error": "Missing end location"}
            }
    else:
        return {
            "reply": "Sorry, please specify 'from' and 'to' locations.",
            "start": {"error": "Missing 'from'"},
            "end": {"error": "Missing 'to'"}
        }

    start = geolocator.geocode(start_location)
    end = geolocator.geocode(end_location)

    if not start or not end:
        return {
            "reply": "Sorry, one or both locations could not be found.",
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
        async with httpx.AsyncClient(timeout=None) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            r = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            content = data.get("response", "").strip()
            content = content.replace("```json", "").replace("```", "").strip()
            itinerary_data = json.loads(content)
            return itinerary_data
    except json.JSONDecodeError:
        return {"error": "Model output was not valid JSON"}
    except Exception as e:
        return {"error": str(e)}

@chat_router.websocket("/ws/ollama")
async def ws_ollama(websocket: WebSocket):
    await websocket.accept()
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            while True:
                incoming = await websocket.receive_text()
                payload_chat = {
                    "model": OLLAMA_MODEL,
                    "messages": [{"role": "user", "content": incoming}],
                    "stream": True
                }
                async with client.stream("POST", f"{OLLAMA_HOST}/api/chat", json=payload_chat) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            if "message" in obj and obj["message"].get("content"):
                                await websocket.send_text(obj["message"]["content"])
                            elif "response" in obj:
                                await websocket.send_text(obj["response"])
                        except Exception:
                            continue
    except WebSocketDisconnect:
        return
