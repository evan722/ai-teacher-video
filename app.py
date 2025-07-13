import os
from datetime import timedelta
import streamlit as st
from openai import OpenAI
import streamlit_js_eval

# === Page Configuration ===
st.set_page_config(page_title="🎓 AI Teacher Assistant", layout="wide")
st.title("📚 AI Teacher Video Generator with Assistant")

# === Setup OpenAI Client ===
if "OPENAI_API_KEY" not in st.secrets:
    st.error("🚨 Please add your OpenAI API key to `.streamlit/secrets.toml` as OPENAI_API_KEY.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === Sidebar File Upload ===
with st.sidebar:
    st.header("📤 Upload Your Files")
    video_file = st.file_uploader("Upload narrated class video (.mp4)", type=["mp4"])
    slides_file = st.file_uploader("Upload slides (PDF, PNG, JPG)", type=["pdf", "png", "jpg"])

# === Main Interface ===
if video_file and slides_file:
    st.success("✅ Files received!")

    # === Save uploaded video to disk ===
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    # === Embed custom video player with ID ===
    st.markdown(f"""
    <video id="classVideo" width="100%" controls>
        <source src="{video_path}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """, unsafe_allow_html=True)

    # === Get current timestamp using JS ===
    js_result = streamlit_js_eval.streamlit_js_eval(
        js_expressions="document.getElementById('classVideo')?.currentTime || 0",
        key="timestamp_key",
        timeout=1000
    )

    if "timestamp" not in st.session_state:
        st.session_state["timestamp"] = 0

    if js_result is not None:
        st.session_state["timestamp"] = int(js_result)

    current_time = st.session_state["timestamp"]
    st.caption(f"⏱️ Current video time: `{str(timedelta(seconds=current_time))}`")

    # === Simulated Slide Context ===
    if current_time < 600:
        slide_context = "This slide is about energy transfer and photosynthesis."
    elif current_time < 1200:
        slide_context = "This slide covers chloroplast structure and function."
    else:
        slide_context = "This slide explains ATP production in mitochondria."

    # === Sidebar Chat Assistant ===
    with st.sidebar:
        st.header("💬 Ask the Teacher")
        user_question = st.text_input("Ask a question about the current topic:")

        if user_question:
            prompt = f"""
You're an AI teacher assistant. The viewer is watching a recorded lesson at `{current_time}` seconds.

They're currently seeing a slide with this content:
---
{slide_context}
---

The viewer asked:
"{user_question}"

Answer in a clear, helpful tone — like a real teacher would in a class.
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an educational assistant embedded in a video lesson."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content.strip()
                st.markdown("#### 📘 AI Teacher’s Answer")
                st.info(answer)
            except Exception as e:
                st.error(f"❌ OpenAI API error: {e}")

else:
    st.warning("⬅️ Please upload both a video and slide file to begin.")
