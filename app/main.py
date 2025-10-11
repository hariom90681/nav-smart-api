# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from app import nav_route
# from app.nav_route import route_router, itinerary_router
#
# app = FastAPI(title="AI Navigation app", version="1.0")
#
# app.mount("/static", StaticFiles(directory="static"), name="static")
#
# # Enable the route
#
# app.include_router(route_router)
# app.include_router(itinerary_router)
#
#
# @app.get("/")
# async def root():
#     return FileResponse('index.html')

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.nav_route import route_router, itinerary_router

app = FastAPI(title="AI Navigation App", version="1.0")

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Serve static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Include routers
app.include_router(route_router)
app.include_router(itinerary_router)

# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "index.html")
