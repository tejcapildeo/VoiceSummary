# config.py
import os
from openai import OpenAI

OPENAI_API_KEY = None

# 1. Try to load from Streamlit Cloud secrets (if running under Streamlit)
try:
    import streamlit as st  # type: ignore

    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    # Not running under Streamlit, or st not available
    pass

# 2. Fallback to .env / environment variables for local development
if OPENAI_API_KEY is None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        # dotenv is optional; ignore if not available
        pass

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is not set. "
        "Set it in Streamlit Cloud secrets (OPENAI_API_KEY) or in a local .env file."
    )

# Shared OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
