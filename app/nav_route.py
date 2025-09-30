import io

import librosa
from fastapi import APIRouter, UploadFile, File

from app.map_prompt import extract_locations, get_coordinates
from app.text_transform import asr

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/get-route")
async def get_route(audio_file: UploadFile = File(...)):
    # Read uploaded bytes
    audio_bytes = await audio_file.read()
    audio_file_obj = io.BytesIO(audio_bytes)

    # Decode audio to numpy (force 16kHz for Whisper)
    audio_array, _ = librosa.load(audio_file_obj, sr=16000, mono=True)

    # Step 1: Transcribe (no sampling_rate arg anymore)
    transcription = asr(audio_array)["text"]

    # Step 2: Extract locations
    locations = extract_locations(transcription)

    if len(locations) < 2:
        return {"error": "Could not detect both start and end locations", "transcription": transcription}

    # Step 3: Geocode
    start = get_coordinates(locations[0])
    end = get_coordinates(locations[1])

    return {
        "transcription": transcription,
        "start": start,
        "end": end
    }