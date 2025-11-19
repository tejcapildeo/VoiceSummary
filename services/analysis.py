# services/analysis.py
import json
from typing import Any, Dict

from config import client


def analyze_transcript(transcript: str) -> Dict[str, Any]:
    """
    Sends the transcript to an LLM and returns structured info:
    - summary_short
    - summary_detailed (list of bullets)
    - decisions
    - action_items (list of {description, owner?, due_date?})
    - open_questions
    """
    system_prompt = """
You are an assistant that analyzes meeting or conversation transcripts.

Given a transcript, you will extract:
1) A short 2-3 sentence summary.
2) A detailed bullet-point summary (5-12 bullets).
3) A list of key decisions or outcomes.
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
Transcript:
\"\"\"{transcript}\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or whichever model you prefer
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        data = {
            "summary_short": "Model returned non-JSON output. See detailed summary.",
            "summary_detailed": [raw_content],
            "decisions": [],
            "action_items": [],
            "open_questions": [],
        }

    data.setdefault("summary_short", "")
    data.setdefault("summary_detailed", [])
    data.setdefault("decisions", [])
    data.setdefault("action_items", [])
    data.setdefault("open_questions", [])

    return data
