import os
import streamlit as st
from moviepy.editor import VideoFileClip
from openai import OpenAI
from moviepy.editor import *
from datetime import timedelta

# === Settings ===
st.set_page_config(page_title="AI Teacher Video Generator", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🎓 AI Teacher Video + Interactive Assistant")

# === Upload Files ===
with st.sidebar:
    st.header("📤 Upload your files")
    video_file = st.file_uploader("Upload class video (MP4)", type=["mp4"])
    slide_file = st.file_uploader("Upload slides (PDF)", type=["pdf"])

if video_file and slide_file:
    st.success("✅ Files uploaded successfully! (processing simulated...)")

    # Simulated pre-generated output (for deployment demo)
    video_url = "https://huggingface.co/spaces/your-repo/video-placeholder.mp4"  # Replace with your own URL

    st.video(video_url, start_time=0)

    # === Timestamp Slider ===
    with st.sidebar:
        st.subheader("⏱️ Video Time Context")
        current_time = st.slider("Approximate video time (seconds)", 0, 2700, step=10)
        st.caption(f"Current time: {str(timedelta(seconds=current_time))}")

    # === Get current slide content (simulated logic) ===
    # You would map this from pre-computed slide-timestamps (based on audio length per slide)
    slide_context = "Photosynthesis and energy conversion" if current_time < 600 else "Chloroplast function and sunlight"

    # === Chat Assistant ===
    with st.sidebar:
        st.header("💬 Ask the Teacher")
        user_q = st.text_input("What would you like to ask?")
        if user_q:
            prompt = f"""
You're an AI teaching assistant embedded in a class video. The user is currently watching a lesson at timestamp {current_time} seconds.
They're learning about this topic:
---
{slide_context}
---
Here is their question:
"{user_q}"

Respond like a teacher giving a thoughtful, helpful explanation. Keep it accessible, clear, and connected to the topic at hand.
"""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an educational video assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content.strip()
            st.markdown("#### 📘 AI Answer")
            st.info(answer)

else:
    st.warning("⬅️ Upload a video and PDF slide deck to begin.")
