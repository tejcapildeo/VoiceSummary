# app.py
import json
from datetime import datetime

import streamlit as st
from audio_recorder_streamlit import audio_recorder

from services.transcription import transcribe_audio
from services.analysis import analyze_transcript


st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Meeting Summarizer")
st.write(
    "Upload a recording of your meeting or important conversation, or record one on the spot, "
    "and this tool will generate a transcript, summary, key decisions, and action items."
)

# Sidebar: instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("---")
    st.markdown(
        "1. **Record** audio using the recorder *or* **upload** an audio file (`.mp3`, `.wav`, `.m4a`).\n"
        "2. Click **Process audio**.\n"
        "3. Review the transcript and AI-generated summary.\n\n"
        "Tip: Keep background noise low for better transcription."
    )

st.markdown("### Choose input")

# Recording widget
st.markdown("#### 🎙️ Record audio")
recorded_audio = audio_recorder(text="Click to record / stop", pause_threshold=2.0)

if recorded_audio:
    st.success("Recorded audio captured.")
    st.audio(recorded_audio, format="audio/wav")

st.markdown("#### 📁 Or upload an audio file")

# File upload
audio_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "wav", "m4a"],
    help="Record your meeting on your phone or laptop, then upload the file here.",
)

process_clicked = st.button("⚙️ Process audio")

if process_clicked:
    # Decide which source to use
    file_bytes = None

    if recorded_audio is not None:
        # Prefer recorded audio if available
        file_bytes = recorded_audio
    elif audio_file is not None:
        file_bytes = audio_file.read()

    if file_bytes is None:
        st.error("Please either record audio or upload an audio file before processing.")
    else:
        # Step 1: Transcription
        with st.spinner("Transcribing audio... This may take a moment."):
            transcript = transcribe_audio(file_bytes)

        if not transcript:
            st.error("Something went wrong during transcription. Please try again.")
        else:
            st.success("✅ Transcription complete!")

            # Show transcript (collapsible)
            with st.expander("📄 Show full transcript", expanded=False):
                st.text_area("Transcript", transcript, height=300)

            # Step 2: Analysis / summarization
            with st.spinner("Analyzing conversation..."):
                result = analyze_transcript(transcript)

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
                        st.markdown(
                            f"- {desc}" + (f"  \n  {meta_str}" if meta_str else "")
                        )
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
            auto_title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            export_data = {
                "title": auto_title,
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
                file_name=f"{auto_title.replace(' ', '_')}.json",
                mime="application/json",
                data=json.dumps(export_data, indent=2),
            )

            # Copyable summary
            st.text_area(
                "Copyable text summary",
                value=(
                    f"{auto_title}\n\n"
                    f"Short summary:\n{export_data['summary_short']}\n\n"
                    f"Decisions:\n" + "\n".join(f"- {d}" for d in export_data["decisions"]) + "\n\n"
                    f"Action items:\n" + "\n".join(
                        f"- {ai.get('description', '')}" for ai in export_data["action_items"]
                    )
                ),
                height=200,
            )
else:
    st.info("Record audio or upload a file, then click **Process audio** to get started.")
