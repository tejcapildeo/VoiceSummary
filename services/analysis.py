# services/analysis.py
import json
from typing import Any, Dict

from config import client


def analyze_transcript(transcript: str, meeting_type: str) -> Dict[str, Any]:
    """
    Sends the transcript to an LLM and returns structured info:
    - summary_short
    - summary_detailed (list of bullets)
    - decisions
    - action_items (list of {description, owner?, due_date?})
    - open_questions
    """
    system_prompt = """
You are an assistant that analyzes meeting transcripts.

Given a transcript, you will extract:
1) A short 2-3 sentence summary.
2) A detailed bullet-point summary (5-12 bullets).
3) A list of key decisions made.
4) A list of action items. 
   Each action item should have:
   - description
   - optional owner (person)
   - optional due date (if mentioned).
5) A list of open questions or unresolved points.

Respond ONLY as valid JSON with this structure:

{
  "summary_short": "string",
  "summary_detailed": ["string", "string"],
  "decisions": ["string", "string"],
  "action_items": [
    {
      "description": "string",
      "owner": "string or null",
      "due_date": "string or null"
    }
  ],
  "open_questions": ["string", "string"]
}
"""

    user_prompt = f"""
Meeting type: {meeting_type}

Transcript:
\"\"\"{transcript}\"\"\"
"""

    response = client.chat.completions.create(
        # Using 40 mini for now
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content

    # Try to parse JSON; if it fails, wrap into a basic structure
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        # Fallback: wrap the raw content in a minimal structure
        data = {
            "summary_short": "Model returned non-JSON output. See detailed summary.",
            "summary_detailed": [raw_content],
            "decisions": [],
            "action_items": [],
            "open_questions": [],
        }

    # Ensure all keys exist
    data.setdefault("summary_short", "")
    data.setdefault("summary_detailed", [])
    data.setdefault("decisions", [])
    data.setdefault("action_items", [])
    data.setdefault("open_questions", [])

    return data
