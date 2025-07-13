import streamlit as st
from datetime import timedelta
from openai import OpenAI

# === App Config ===
st.set_page_config(page_title="🎓 AI Teacher Assistant", layout="wide")
st.title("📚 AI Teacher Video Generator with Assistant")

# === Setup OpenAI ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === Sidebar Upload ===
with st.sidebar:
    st.header("📤 Upload your files")
    video_file = st.file_uploader("Upload final narrated class video (.mp4)", type=["mp4"])
    slides_file = st.file_uploader("Upload slides (PDF or any format)", type=["pdf", "png", "jpg"])

# === Main Area ===
if video_file and slides_file:
    st.success("✅ Files received!")

    # Save video temporarily to play it
    with open("uploaded_video.mp4", "wb") as f:
        f.write(video_file.read())

    st.video("uploaded_video.mp4", start_time=0)

    # Simulate slide context for now
    with st.sidebar:
        st.subheader("⏱️ Approximate Video Time")
        current_time = st.slider("Set current video timestamp (seconds)", 0, 2700, step=10)
        st.caption(f"📍 Current time: {str(timedelta(seconds=current_time))}")

    # Simulate slide content (replace with actual logic if you process slides)
    slide_context = (
        "This slide is about energy transfer and photosynthesis."
        if current_time < 600 else
        "This slide covers chloroplast structure and function."
    )

    # === Sidebar Chat Assistant ===
    with st.sidebar:
        st.header("💬 Ask the Teacher")
        user_question = st.text_input("Ask a question based on the current slide:")

        if user_question:
            prompt = f"""
You're an AI teacher assistant. The viewer is watching a lesson at {current_time} seconds into the video.

They are currently viewing a slide with this content:
---
{slide_context}
---

The viewer asked:
"{user_question}"

Respond in a clear, helpful, and friendly tone, as if you're a real teacher explaining in context.
"""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an educational assistant embedded in a class video."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content.strip()
            st.markdown("#### 📘 AI Teacher’s Answer")
            st.info(answer)

else:
    st.warning("⬅️ Please upload both a video and slide file to begin.")
