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
st.set_page_config(page_title="RAMAN AI STUDIO - THE MASTERPIECE", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #030303; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - THE MASTERPIECE")
st.markdown("<p style='text-align: center; color: #888888;'>परफेक्ट ॲक्शन, अचूक पात्र आणि १००% मेमरी इंजिन!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. UI ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा (Language):", ["Marathi", "Hindi", "English"])
    st.success("🛡️ **Anti-Hallucination Brain Active:** आता AI ला मराठीवरून कन्फ्युजन होणार नाही. ते फक्त अचूक 'इंग्रजी' कमांड बनवून १००% ओरिजिनल गरुड आणि वाघच दाखवेल!")
with col2:
    script_text = st.text_area("२. परफेक्ट स्क्रिप्ट टाका:", height=200, placeholder="उदा. एक भव्य गरुड आकाशात उंच भरारी घेत होता. तिथे एक पट्टेदार वाघ शांतपणे पाणी पीत होता.")

async def generate_audio_segment(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 3. Video Generation Engine ---
if st.button("🚀 Generate 32K Perfect Action Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("🧠 AI तुमचा डिरेक्टर मोड सेट करत आहे... (कृपया शांत राहा, उत्तम व्हिडिओ बनत आहे)"):
            try:
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही.")
                    st.stop()
                
                video_clips = []
                
                # VISUAL STYLE (100% English)
                VISUAL_STYLE = "Ultra-high-definition, cinematic masterpiece, 32K resolution, National Geographic documentary style, flawless physical accuracy, photorealistic physics, cinematic lighting, no text, no watermark."
                
                # MEMORY VARIABLES
                active_subject = "Beautiful Cinematic landscape"
                active_voice = "mr-IN-ManoharNeural" if language == "Marathi" else "hi-IN-MadhurNeural"
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    s_lower = sentence.lower()
                    
                    # 1. SUBJECT DETECTION (मागील पात्राला लक्षात ठेवेल)
                    if any(w in s_lower for w in ["गरुड", "गरूड", "eagle"]):
                        active_subject = "A Majestic Bald Eagle"
                        active_voice = "mr-IN-ManoharNeural" if language == "Marathi" else "hi-IN-MadhurNeural"
                    elif any(w in s_lower for w in ["वाघ", "tiger"]):
                        active_subject = "A fierce wild Bengal Tiger"
                    elif any(w in s_lower for w in ["सिंह", "lion"]):
                        active_subject = "A wild African Lion"
                    elif any(w in s_lower for w in ["घुबड", "owl"]):
                        active_subject = "A wild night owl bird"
                    elif any(w in s_lower for w in ["स्त्री", "मुलगी", "आई", "ती", "woman", "girl", "she"]):
                        active_subject = "A beautiful Indian woman in traditional attire"
                        active_voice = "mr-IN-AarohiNeural" if language == "Marathi" else "hi-IN-SwaraNeural"
                    elif any(w in s_lower for w in ["माणूस", "मुलगा", "तो", "man", "boy", "he"]):
                        active_subject = "A rugged Indian man"
                    
                    # 2. ACTION TRANSLATOR (मराठीवरून इंग्रजी ॲक्शन)
                    action = "cinematic action shot, detailed"
                    if any(w in s_lower for w in ["उड", "भरारी", "आकाशात", "पंख", "ढग"]):
                        action = "flying high in the sky with spread wings, dynamic motion"
                    elif any(w in s_lower for w in ["पाणी", "नदी", "काठी", "पीत"]):
                        action = "drinking water from a river in a dense forest"
                    elif any(w in s_lower for w in ["डरकाळी", "ओरड", "भयंकर", "पाहिले"]):
                        action = "roaring aggressively, fierce expression, looking angry, close-up face"
                    elif any(w in s_lower for w in ["शांत", "बस", "झाड"]):
                        action = "sitting calmly on a branch, resting"
                    elif any(w in s_lower for w in ["चाल", "पळ"]):
                        action = "walking dynamically, intense cinematic scene"

                    # 3. Audio Generation
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio_segment(sentence, active_voice, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 4. Image Generation (100% PURE ENGLISH PROMPT)
                    # आता इमेज जनरेटरला एकही मराठी शब्द दिसणार नाही!
                    final_image_prompt = f"{active_subject}, {action}. {VISUAL_STYLE}"
                    encoded_query = urllib.parse.quote(final_image_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                    
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 5. Motion (Cinematic Zoom)
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.015 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 सर्व सीन्सची व्यावसायिक जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                
                output_video = "Raman_Perfect_Action_Final.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा १००% परिपूर्ण आणि हुबेहूब व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
