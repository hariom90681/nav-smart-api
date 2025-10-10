from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app import nav_route

app = FastAPI(title="AI Navigation app", version="1.0")

# This line "mounts" the static directory, making index.html available
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the API endpoints from your other file
app.include_router(nav_route.router)

# This new root endpoint serves your index.html file as the homepage
@app.get("/")
async def root():
    return FileResponse('static/index.html')