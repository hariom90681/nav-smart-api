import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.nav_route import route_router, itinerary_router, chat_router

app = FastAPI(title="AI Navigation App", version="1.0")

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Serve static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Include routers
app.include_router(route_router)
app.include_router(itinerary_router)
app.include_router(chat_router)

# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/config.js")
async def serve_config_js():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    content = f"window.GOOGLE_MAPS_API_KEY='{api_key}';"
    return Response(content, media_type="application/javascript")
