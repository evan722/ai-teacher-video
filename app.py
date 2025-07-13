import streamlit as st
import streamlit.components.v1 as components
from datetime import timedelta
from openai import OpenAI
import base64

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

    # Save video temporarily and encode to base64 for HTML
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.read())
    video_base64 = base64.b64encode(open(video_path, 'rb').read()).decode()

    # Inject HTML video player with JS to track timestamp
    st.markdown("### 🎥 Class Video with Smart Assistant")
    components.html(f"""
        <video id="classVideo" width="700" controls>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
        <script>
            const streamlitSendTime = () => {{
                const vid = document.getElementById("classVideo");
                setInterval(() => {{
                    window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: Math.floor(vid.currentTime) }}, '*');
                }}, 1000);
            }};
            streamlitSendTime();
        </script>
    """, height=400)

    # === Read synced timestamp ===
    current_time = st.experimental_get_query_params().get("timestamp", [0])[0]
    current_time = int(current_time)

    st.caption(f"📍 Current video time: {str(timedelta(seconds=current_time))}")

    # Simulated context by time
    if current_time < 600:
        slide_context = "This slide is about energy transfer and photosynthesis."
    elif current_time < 1200:
        slide_context = "This slide covers chloroplast structure and function."
    else:
        slide_context = "This slide reviews cellular respiration and ATP production."

    # === Chat Assistant ===
    with st.sidebar:
        st.header("💬 Ask the Teacher")
        user_question = st.text_input("Ask a question about what you're seeing:")

        if user_question:
            prompt = f"""
You are an AI teacher assistant. The user is watching a lesson at {current_time} seconds.

They are viewing this slide:
---
{slide_context}
---

They asked:
"{user_question}"

Give a helpful, teacher-like explanation that fits the context.
"""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a patient, insightful teacher assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.markdown("#### 📘 AI Teacher’s Answer")
            st.info(response.choices[0].message.content.strip())

else:
    st.warning("⬅️ Please upload both a video and slide file to begin.")
