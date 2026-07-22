# --- Error Patch for MoviePy ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import streamlit as st
import asyncio
import edge_tts
import urllib.parse
import requests
import re
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- 1. App Configuration ---
st.set_page_config(page_title="RAMAN AI STUDIO - MULTI SCENE", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - DIRECTOR'S CUT")
st.markdown("<p style='text-align: center; color: #888888;'>१ क्लिक. ऑटोमॅटिक मल्टी-सीन व्हिडिओ. झिरो API Key.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. Clean 2-Input Interface ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा (Language):", ["Marathi", "Hindi", "English"])
with col2:
    script_text = st.text_area("२. परफेक्ट स्क्रिप्ट टाका:", height=180, placeholder="तुमची स्क्रिप्ट इथे पेस्ट करा. (वाक्यांनुसार दृश्ये बदलतील!)")

# --- 3. Smart Voice & Scene Engine ---
def get_voice(lang, text):
    text_lower = text.lower()
    if lang == "Marathi":
        return "mr-IN-AarohiNeural" if any(w in text_lower for w in ["मुलगी", "ती", "स्त्री"]) else "mr-IN-ManoharNeural"
    elif lang == "Hindi":
        return "hi-IN-SwaraNeural" if any(w in text_lower for w in ["लड़की", "औरत", "वह"]) else "hi-IN-MadhurNeural"
    else:
        return "en-US-AriaNeural" if any(w in text_lower for w in ["girl", "woman", "she"]) else "en-US-ChristopherNeural"

async def generate_audio_segment(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 1-Click Multi-Scene Execution ---
if st.button("🚀 Generate Multi-Scene Auto Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("🎬 RAMAN AI STUDIO सीन्सचे विश्लेषण करत आहे... (यात थोडा वेळ लागू शकतो)"):
            try:
                # स्क्रिप्टला वाक्यांमध्ये तोडणे (Splitting script into scenes)
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही. कृपया नीट वाक्ये टाका.")
                    st.stop()
                
                voice_model = get_voice(language, script_text)
                st.success(f"🎙️ Voice Selected: **{voice_model}** | 🎬 Total Scenes Detected: **{len(sentences)}**")
                
                video_clips = []
                
                for i, sentence in enumerate(sentences):
                    st.text(f"⚙️ Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    # 1. Generate Audio for this specific sentence
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio_segment(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 2. Generate Contextual Image for this specific sentence
                    # (Translating basic keywords implicitly by asking Pollinations for cinematic shot of the sentence context)
                    visual_query = f"{sentence}, highly detailed cinematic masterpiece, 8k resolution, professional film lighting"
                    encoded_query = urllib.parse.quote(visual_query)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                    
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 3. Create Scene Clip with Zoom Effect
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.015 * t) # Cinematic Slow Zoom
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                # 4. Stitch All Scenes Together
                st.info("🔄 सर्व सीन्स एकत्र जोडून फायनल व्हिडिओ बनवत आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                
                output_video = "Raman_AI_Studio_MultiScene.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा फायनल मल्टी-सीन व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                # Cleanup memory
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
