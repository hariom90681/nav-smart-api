from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app import nav_route
from app.nav_route import route_router, itinerary_router

app = FastAPI(title="AI Navigation app", version="1.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable the route

app.include_router(route_router)
app.include_router(itinerary_router)


@app.get("/")
async def root():
    return FileResponse('index.html')