# app.py

import os
import asyncio
import nest_asyncio
from moviepy.editor import *
from pydub import AudioSegment
from faster_whisper import WhisperModel
from pdf2image import convert_from_path
import pytesseract
import edge_tts
from openai import OpenAI

nest_asyncio.apply()

# === SETTINGS ===
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# === STEP 1: Transcribe video ===
def transcribe_video(video_path):
    model = WhisperModel("base")
    segments, _ = model.transcribe(video_path)
    transcript = " ".join([seg.text for seg in segments])
    with open("transcript.txt", "w") as f:
        f.write(transcript)
    return transcript

# === STEP 2: Extract slides from PDF ===
def extract_slides(pdf_path):
    images = convert_from_path(pdf_path)
    slide_texts = []
    for i, img in enumerate(images):
        img.save(f"slide_{i+1}.png")
        text = pytesseract.image_to_string(img)
        slide_texts.append(text.strip())
    return slide_texts

# === STEP 3: Generate narration scripts ===
def generate_scripts(slide_texts, teaching_style):
    teacher_scripts = []
    for i, slide_text in enumerate(slide_texts):
        prompt = f"""
You are a real teacher presenting a lesson. Here's the content of a slide:
---
{slide_text}
---
And here’s the teaching tone from a real classroom transcript:
---
{teaching_style[:1500]}
---

Write a natural, spoken narration for this slide. Speak clearly, avoid fake names or students.
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a teacher recording a video lesson."},
                {"role": "user", "content": prompt}
            ]
        )
        narration = response.choices[0].message.content.strip()
        teacher_scripts.append(narration)
        print(f"✅ Slide {i+1} script done.")
    return teacher_scripts

# === STEP 4: Generate audio with edge-tts ===
async def generate_audio(teacher_scripts):
    audio_paths = []
    for i, script in enumerate(teacher_scripts):
        filename = f"slide_audio_{i+1}.mp3"
        try:
            communicate = edge_tts.Communicate(script, "en-US-JennyNeural")
            await communicate.save(filename)
            audio_paths.append(filename)
            print(f"✅ Slide {i+1} audio generated.")
        except Exception as e:
            print(f"❌ Audio error: {e}")
    return audio_paths

# === STEP 5: Calculate timestamps ===
def get_timestamps(audio_paths):
    timestamps = [0]
    for audio_file in audio_paths:
        seg = AudioSegment.from_file(audio_file)
        duration = len(seg) / 1000
        timestamps.append(timestamps[-1] + duration)
    return timestamps

# === STEP 6: Stitch video ===
def build_video(audio_paths, num_slides):
    final_clips = []
    for i in range(num_slides):
        img_path = f"slide_{i+1}.png"
        audio_path = f"slide_audio_{i+1}.mp3"
        img_clip = ImageClip(img_path).set_duration(AudioFileClip(audio_path).duration)
        img_clip = img_clip.set_audio(AudioFileClip(audio_path))
        final_clips.append(img_clip)
    video = concatenate_videoclips(final_clips, method="compose")
    video.write_videofile("final_teacher_video.mp4", fps=1)
