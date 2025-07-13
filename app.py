import os
from datetime import timedelta
import streamlit as st
from openai import OpenAI
import streamlit_js_eval

# === App Config ===
st.set_page_config(page_title="🎓 AI Teacher Assistant", layout="wide")
st.title("📚 AI Teacher Video Generator with Assistant")

# === Setup OpenAI (expects key in .streamlit/secrets.toml as OPENAI_API_KEY)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("❌ Please add your OpenAI key to `.streamlit/secrets.toml` as `OPENAI_API_KEY`")
    st.stop()

# === Sidebar Upload ===
with st.sidebar:
    st.header("📤 Upload your files")
    video_file = st.file_uploader("Upload final narrated class video (.mp4)", type=["mp4"])
    slides_file = st.file_uploader("Upload slides (PDF or any format)", type=["pdf", "png", "jpg"])

# === Main Area ===
if video_file and slides_file:
    st.success("✅ Files received!")

    # Read video into memory (more compatible than writing to disk)
    video_bytes = video_file.read()
    st.video(video_bytes)

    # === JS Evaluation to get current video time (auto-updating)
    js_result = streamlit_js_eval.streamlit_js_eval(
        js_expressions="document.querySelector('video')?.currentTime || 0",
        key="video_time_sync",
        timeout=1000,
    )

    # Track current video time
    if "timestamp" not in st.session_state:
        st.session_state["timestamp"] = 0
    if js_result is not None:
        st.session_state["timestamp"] = int(js_result)

    current_time = st.session_state["timestamp"]
    st.caption(f"⏱️ Current video time: `{str(timedelta(seconds=current_time))}`")

    # === Simulated slide context (you can replace with real slide mapping)
    if current_time < 600:
        slide_context = "This slide explains the process of photosynthesis and energy flow in plants."
    elif current_time < 1200:
        slide_context = "This slide introduces the structure and function of chloroplasts."
    else:
        slide_context = "This slide explores how mitochondria generate ATP through cellular respiration."

    # === Sidebar Chat Assistant ===
    with st.sidebar:
        st.header("💬 Ask the Teacher")
        user_question = st.text_input("Ask a question about the current lesson:")

        if user_question:
            prompt = f"""
You are an AI teacher assistant. A viewer is watching a lesson at `{current_time}` seconds into the video.

They are currently viewing this content:
---
{slide_context}
---

They asked:
"{user_question}"

Answer like a thoughtful teacher: clear, friendly, and informative. Include helpful examples if needed.
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful, knowledgeable teaching assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content.strip()
                st.markdown("#### 📘 AI Teacher’s Answer")
                st.info(answer)
            except Exception as e:
                st.error(f"❌ OpenAI error: {e}")
else:
    st.warning("⬅️ Please upload both a video and a slide file to begin.")
