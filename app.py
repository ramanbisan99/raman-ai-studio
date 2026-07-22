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
st.set_page_config(page_title="RAMAN AI STUDIO - 32K PRO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #030303; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - 32K ACTION PRO")
st.markdown("<p style='text-align: center; color: #888888;'>परफेक्ट ॲक्शन, अचूक पात्र आणि १००% स्वयंचलित नॅशनल जिओग्राफिक स्टाईल!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. 100% Automated UI ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा (Language):", ["Marathi", "Hindi", "English"])
    st.success("🤖 **Smart Subject Engine Active:** हा मेंदू आता अचूक प्राणी, पक्षी किंवा माणूस ओळखेल आणि माणसाचे चेहरे मध्येच आणणार नाही!")
with col2:
    script_text = st.text_area("२. परफेक्ट स्क्रिप्ट टाका:", height=200, placeholder="उदा. एक गरुड आकाशात उडत होता. तिथे एक वाघ पाणी पीत होता.")

# --- 3. Smart Subject & Voice Engine ---
def analyze_scene(sentence, lang):
    s_lower = sentence.lower()
    subject = "Cinematic scenery, high quality"
    voice = "mr-IN-ManoharNeural" # Default Marathi Male

    # 1. पक्षी आणि प्राणी ओळखणे (Subject Extraction)
    if any(w in s_lower for w in ["गरुड", "गरूड", "eagle"]): 
        subject = "A Majestic Bald Eagle bird"
    elif any(w in s_lower for w in ["वाघ", "tiger"]): 
        subject = "A fierce wild Bengal Tiger"
    elif any(w in s_lower for w in ["सिंह", "lion"]): 
        subject = "A wild African Lion"
    elif any(w in s_lower for w in ["घुबड", "owl"]): 
        subject = "A wild night owl bird"
    elif any(w in s_lower for w in ["हत्ती", "elephant"]): 
        subject = "A wild elephant"
    elif any(w in s_lower for w in ["हरीण", "हरिण", "deer"]): 
        subject = "A wild beautiful deer"
        
    # 2. माणसे ओळखणे
    elif any(w in s_lower for w in ["स्त्री", "मुलगी", "आई", "ती", "woman", "girl", "she", "her"]): 
        subject = "A beautiful Indian woman"
        voice = "mr-IN-AarohiNeural"
    elif any(w in s_lower for w in ["म्हातारी", "आजी"]): 
        subject = "An old Indian woman"
        voice = "mr-IN-AarohiNeural"
    elif any(w in s_lower for w in ["माणूस", "मुलगा", "तो", "man", "boy", "he"]): 
        subject = "An Indian man"
    elif any(w in s_lower for w in ["म्हातारा", "आजोबा"]): 
        subject = "An old Indian man"

    # Language Voice overrides
    if lang == "Hindi":
        voice = "hi-IN-SwaraNeural" if "woman" in subject or "Aarohi" in voice else "hi-IN-MadhurNeural"
    elif lang == "English":
        voice = "en-US-AriaNeural" if "woman" in subject or "Aarohi" in voice else "en-US-ChristopherNeural"

    return subject, voice

async def generate_audio_segment(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 32K Video Generation Engine ---
if st.button("🚀 Generate 32K Perfect Action Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("🧠 AI अचूक पात्र ओळखून दृश्ये बनवत आहे..."):
            try:
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही. कृपया पूर्णविराम असलेली वाक्ये टाका.")
                    st.stop()
                
                video_clips = []
                
                # Raman's Optimized 32K Cinematic Style
                VISUAL_STYLE = "Ultra-high-definition, cinematic masterpiece, 32K resolution, National Geographic documentary style, flawless physical accuracy, photorealistic physics, cinematic lighting, no text, no watermark."
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    # अचूक पात्र आणि आवाज मिळवणे
                    scene_subject, voice_model = analyze_scene(sentence, language)
                    
                    # 1. ऑडिओ
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio_segment(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 2. ॲक्शन इमेज (Subject + Action + Style)
                    # आता AI ला सर्वात आधी कळेल की विषय माणूस नसून गरुड किंवा वाघ आहे!
                    final_image_prompt = f"Main Subject: {scene_subject}. Action taking place: {sentence}. {VISUAL_STYLE}"
                    
                    encoded_query = urllib.parse.quote(final_image_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                    
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 3. सिनेमॅटिक मोशन
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
                
                st.success("✅ तुमचा डायनॅमिक ॲक्शन असलेला व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                # मेमरी क्लिनअप
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
