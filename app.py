# app.py
import json
from datetime import datetime

import streamlit as st

from services.transcription import transcribe_audio
from services.analysis import analyze_transcript


st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Meeting Summarizer")
st.write(
    "Upload a recording of your meeting or important conversation, and this tool "
    "will generate a transcript, summary, key decisions, and action items."
)

# Sidebar configuration / info
with st.sidebar:
    st.header("Instructions")
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown(
        "1. Upload an audio file (`.mp3`, `.wav`, `.m4a`).\n"
        "2. Click **Process meeting**.\n"
        "3. Review the transcript and AI-generated summary."
    )

# Main UI
audio_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "wav", "m4a"],
    help="Record your meeting on your phone or laptop, then upload the file here.",
)

process_clicked = st.button("⚙️ Process meeting")

if process_clicked:
    if audio_file is None:
        st.error("Please upload an audio file first.")
    else:
        # Step 1: Transcription
        with st.spinner("Transcribing audio... This may take a moment."):
            transcript = transcribe_audio(audio_file)

        if not transcript:
            st.error("Something went wrong during transcription. Please try again.")
        else:
            st.success("✅ Transcription complete!")

            # Show transcript (collapsible)
            with st.expander("📄 Show full transcript", expanded=False):
                st.text_area("Transcript", transcript, height=300)

            # Step 2: Analysis / summarization
            with st.spinner("Analyzing meeting..."):
                result = analyze_transcript(transcript, meeting_type)

            st.success("✅ Analysis complete!")

            # Layout: two columns for a bit nicer look
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📝 Short Summary")
                st.write(result.get("summary_short", ""))

                st.subheader("🔍 Detailed Summary")
                detailed = result.get("summary_detailed", [])
                if detailed:
                    for bullet in detailed:
                        st.markdown(f"- {bullet}")
                else:
                    st.write("No detailed summary available.")

            with col2:
                st.subheader("✅ Decisions")
                decisions = result.get("decisions", [])
                if decisions:
                    for d in decisions:
                        st.markdown(f"- {d}")
                else:
                    st.write("No explicit decisions detected.")

                st.subheader("📌 Action Items")
                action_items = result.get("action_items", [])
                if action_items:
                    for item in action_items:
                        desc = item.get("description", "")
                        owner = item.get("owner")
                        due = item.get("due_date")
                        meta = []
                        if owner:
                            meta.append(f"Owner: **{owner}**")
                        if due:
                            meta.append(f"Due: **{due}**")
                        meta_str = " | ".join(meta)
                        st.markdown(f"- {desc}" + (f"  \n  {meta_str}" if meta_str else ""))
                else:
                    st.write("No action items detected.")

                st.subheader("❓ Open Questions")
                open_qs = result.get("open_questions", [])
                if open_qs:
                    for q in open_qs:
                        st.markdown(f"- {q}")
                else:
                    st.write("No open questions detected.")

            # Prepare export data
            export_title = meeting_title or "Untitled meeting"
            export_data = {
                "title": export_title,
                "meeting_type": meeting_type,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "transcript": transcript,
                "summary_short": result.get("summary_short", ""),
                "summary_detailed": result.get("summary_detailed", []),
                "decisions": result.get("decisions", []),
                "action_items": result.get("action_items", []),
                "open_questions": result.get("open_questions", []),
            }

            # Download as JSON
            st.markdown("---")
            st.subheader("📥 Export")
            st.download_button(
                label="💾 Download summary as JSON",
                file_name=f"{export_title.replace(' ', '_')}_{datetime.now().date()}.json",
                mime="application/json",
                data=json.dumps(export_data, indent=2),
            )

            # copyable text summary
            st.text_area(
                "Copyable text summary",
                value=f"{export_title}\n\nShort summary:\n{export_data['summary_short']}\n\n"
                      f"Decisions:\n" + "\n".join(f"- {d}" for d in export_data["decisions"]) + "\n\n"
                      f"Action items:\n" + "\n".join(
                          f"- {ai.get('description', '')}" for ai in export_data["action_items"]
                      ),
                height=200,
            )
else:
    st.info("Upload an audio file and click **Process meeting** to get started.")
