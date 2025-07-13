import os
from datetime import timedelta
import streamlit as st
from openai import OpenAI

# === App Config ===
st.set_page_config(page_title="🎓 AI Teacher Assistant", layout="wide")
st.title("📚 AI Teacher Video Generator with Assistant")

# === Setup OpenAI ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Add to .streamlit/secrets.toml

# === Sidebar Upload ===
with st.sidebar:
    st.header("📤 Upload your files")
    video_file = st.file_uploader("🎞️ Upload narrated class video (.mp4)", type=["mp4"])
    slides_file = st.file_uploader("🖼️ Upload slides (PDF or image)", type=["pdf", "png", "jpg"])

# === Main Area ===
if video_file and slides_file:
    st.success("✅ Files received!")

    # === Play Video (streamlit will handle buffering)
    st.video(video_file)

    # === Fallback Manual Time Slider (since we can’t track JS <video> state in Streamlit Cloud)
    with st.sidebar:
        st.subheader("⏱️ Set Video Time (seconds)")
        current_time = st.slider("Pick your current time in the video", 0, 2700, step=10)
        st.caption(f"📍 Current time: {str(timedelta(seconds=current_time))}")

    # === Simulated slide content (replace with real slide mapping later)
    if current_time < 600:
        slide_context = "This slide is about energy transfer and photosynthesis."
    elif current_time < 1200:
        slide_context = "This slide covers chloroplast structure and function."
    else:
        slide_context = "This slide explains ATP production in mitochondria."

    # === Chat Assistant
    with st.sidebar:
        st.header("💬 Ask the Teacher")
        user_question = st.text_input("Ask a question about the current slide:")

        if user_question:
            prompt = f"""
You're an AI teacher assistant. The viewer is watching a recorded lesson at `{current_time}` seconds.

They are currently learning:
---
{slide_context}
---

The viewer asked:
"{user_question}"

Please respond like a knowledgeable, friendly teacher. Use examples, be clear and engaging.
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an educational assistant embedded in a recorded class video."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content.strip()
                st.markdown("#### 📘 AI Teacher’s Answer")
                st.info(answer)
            except Exception as e:
                st.error(f"❌ Chat error: {e}")

else:
    st.warning("⬅️ Please upload both a video and slide file to begin.")
