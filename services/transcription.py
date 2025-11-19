# services/transcription.py
import tempfile
from typing import Optional

from config import client


def transcribe_audio(file_bytes: bytes) -> Optional[str]:
    """
    Takes raw audio bytes and returns a transcript string.
    Returns None if transcription fails.
    """
    try:
        # Write to a temporary file so the OpenAI SDK can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Call the transcription model
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",  # adjust if needed
                file=audio,
            )

        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
