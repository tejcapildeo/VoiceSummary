# services/transcription.py
import tempfile
from typing import Optional

from config import client


def transcribe_audio(uploaded_file) -> Optional[str]:
    """
    Takes a Streamlit UploadedFile object and returns a transcript string.
    Returns None if transcription fails.
    """
    try:
        #reading the uploaded file
        file_bytes = uploaded_file.read()

        # Write to a temporary file so the OpenAI SDK can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Using the whisper1 transcription model
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
            )
        return transcription.text

    except Exception as e:
        #might wanna change this to logging instead of printing
        print(f"Error during transcription: {e}")
        return None
