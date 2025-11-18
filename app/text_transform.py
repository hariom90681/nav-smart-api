import io
from transformers import pipeline

asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",
    generate_kwargs={"task": "translate"}  # force English output
)

def audio_bytes_to_text(audio_bytes: bytes) -> str:
    """
    Convert audio bytes to transcribed text using Whisper.
    Returns transcription as a string.
    """
    audio_file = io.BytesIO(audio_bytes)  
    result = asr(audio_file)
    return result["text"]
