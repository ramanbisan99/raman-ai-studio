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
st.set_page_config(page_title="RAMAN AI STUDIO - AUTO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - 100% AUTO")
st.markdown("<p style='text-align: center; color: #888888;'>फक्त स्क्रिप्ट टाका. AI स्वतः पात्र ओळखेल, व्हॉईस निवडेल आणि कन्सिस्टंट व्हिडिओ बनवेल!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. 100% Automated UI (Only 2 Inputs) ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. व्हिडिओची भाषा (Language):", ["Marathi", "Hindi", "English"])
    st.success("🤖 **AI Brain Active:** हा मोड स्क्रिप्ट वाचून पात्र, ॲक्शन आणि व्हॉईस स्वतः ठरवतो. कोणतेही API किंवा मॅन्युअल सेटिंग्स लागत नाहीत!")
with col2:
    script_text = st.text_area("२. परफेक्ट स्क्रिप्ट टाका:", height=200, placeholder="तुमची स्क्रिप्ट इथे पेस्ट करा. (उदा. एक गरुड आकाशात उंच भरारी घेत होता...)")

# --- 3. The "Smart AI Brain" (Auto Context & Character Extractor) ---
def auto_extract_brain(text, lang):
    text_lower = text.lower()
    
    # A) Auto Voice Detection (लिंगानुसार आणि पात्रांनुसार)
    female_words = ["मुलगी", "स्त्री", "ती", "आई", "आजी", "लड़की", "औरत", "महिला", "she", "her", "woman", "girl", "राणी"]
    is_female = any(w in text_lower for w in female_words)
    
    if lang == "Marathi":
        voice = "mr-IN-AarohiNeural" if is_female else "mr-IN-ManoharNeural"
    elif lang == "Hindi":
        voice = "hi-IN-SwaraNeural" if is_female else "hi-IN-MadhurNeural"
    else:
        voice = "en-US-AriaNeural" if is_female else "en-US-ChristopherNeural"

    # B) Auto Character Lock (स्क्रिप्ट वाचून स्वतः इंग्रजी प्रॉम्प्ट बनवणे)
    if any(w in text_lower for w in ["गरूड", "गरुड", "eagle"]):
        char_lock = "Majestic Bald Eagle, highly detailed feathers, sharp beak, wildlife photography"
    elif any(w in text_lower for w in ["वाघ", "tiger", "शेर"]):
        char_lock = "Fierce Royal Bengal Tiger, highly detailed fur, wildlife photography"
    elif any(w in text_lower for w in ["सिंह", "lion"]):
        char_lock = "Wild African Lion, majestic mane, national geographic style"
    elif any(w in text_lower for w in ["म्हातारी", "old woman", "बुजुर्ग महिला", "आजी"]):
        char_lock = "Old Indian woman, traditional authentic saree, wrinkled expressive face, cinematic portrait"
    elif any(w in text_lower for w in ["म्हातारा", "old man", "बुजुर्ग", "आजोबा"]):
        char_lock = "Old Indian man, traditional rural clothes, cinematic portrait"
    elif any(w in text_lower for w in ["मुलगी", "लड़की", "girl"]):
        char_lock = "Young beautiful Indian girl, authentic traditional dress, cinematic portrait"
    elif any(w in text_lower for w in ["मुलगा", "लड़का", "boy"]):
        char_lock = "Young Indian boy, expressive face, cinematic portrait"
    elif any(w in text_lower for w in ["राजा", "king", "महाराज", "शिवाजी"]):
        char_lock = "Indian King, royal historical attire, cinematic jewelry, warrior look"
    else:
        # जर काहीच सापडले नाही, तर जनरल सिनेमॅटिक फोकस
        char_lock = "Highly detailed main subject, photorealistic, 8k resolution"
        
    return voice, char_lock

async def generate_audio_segment(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 1-Click Multi-Scene Execution ---
if st.button("🚀 Generate Auto Masterpiece"):
    if not script_text.strip():
        st.warning("⚠️ कृपया व्हिडिओ बनवण्यासाठी स्क्रिप्ट टाका.")
    else:
        with st.spinner("🧠 AI तुमची स्क्रिप्ट वाचत आहे आणि सीन्स तयार करत आहे..."):
            try:
                # स्क्रिप्टला वाक्यांमध्ये तोडणे
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही. कृपया पूर्णविराम असलेली वाक्ये टाका.")
                    st.stop()
                
                # AI Brain Call
                voice_model, auto_char_lock = auto_extract_brain(script_text, language)
                st.success(f"🎙️ Auto Voice: **{voice_model}** | 🔒 Auto Character Lock: **{auto_char_lock}**")
                
                video_clips = []
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} तयार होत आहे...")
                    
                    # 1. ऑडिओ जनरेशन
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio_segment(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 2. ऑटोमॅटिक इमेज जनरेशन (Auto Character Lock + Sentence Context)
                    visual_query = f"{auto_char_lock}, action: {sentence}, highly detailed cinematic masterpiece, 8k resolution, professional film lighting"
                    encoded_query = urllib.parse.quote(visual_query)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                    
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 3. सिनेमॅटिक कॅमेरा मोशन
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.015 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 सर्व सीन्स एकत्र जोडले जात आहेत...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                
                output_video = "Raman_100_Auto_Final.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा १००% ऑटोमॅटिक व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
