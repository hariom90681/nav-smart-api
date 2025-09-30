import io
from transformers import pipeline

# Load the model once (reuse it for multiple calls)
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
    audio_file = io.BytesIO(audio_bytes)  # convert bytes to file-like object
    result = asr(audio_file)
    return result["text"]
