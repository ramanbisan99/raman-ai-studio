import streamlit as st
import asyncio
import edge_tts
import urllib.parse
import requests
import re
from moviepy.editor import ImageClip, AudioFileClip

# --- 1. App Configuration ---
st.set_page_config(page_title="Raman AI STUDIO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-transform: uppercase; text-align: center; font-family: 'Arial Black', sans-serif;}
    h2, h3 { color: #FFFFFF; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 5px; border: none; padding: 10px;}
    .stButton>button:hover { background-color: #B20710; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO")
st.write("१ क्लिकमध्ये अनलिमिटेड प्रोफेशनल व्हिडिओ. (Auto-Voice Detection & Zero Token)")

# --- 2. Inputs ---
col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा (Language):", ["Marathi", "Hindi", "English"])
    char_prompt = st.text_input("२. मुख्य पात्र (उदा. Indian boy, old woman):", placeholder="Enter character details...")
    action_details = st.text_input("३. सिनेमॅटिक ॲक्शन (True Action):", placeholder="Talking with hand gestures, walking...")

with col2:
    script_text = st.text_area("४. परफेक्ट स्क्रिप्ट टाका:", height=195, placeholder="स्क्रिप्ट टाका. ॲप स्वतः मुलगा/मुलगी ओळखेल...")

# --- 3. Auto-Voice Detection Brain (Kill Critic Logic) ---
def auto_detect_voice(text, lang):
    text = text.lower()
    
    if lang == "Marathi":
        if re.search(r'\b(मुलगा|पोरगा|boy)\b', text): return "mr-IN-ManoharNeural" 
        elif re.search(r'\b(मुलगी|पोरगी|ती|स्त्री|girl)\b', text): return "mr-IN-AarohiNeural" 
        else: return "mr-IN-ManoharNeural" 
        
    elif lang == "Hindi":
        if re.search(r'\b(लडका|आदमी|वह|रहा)\b', text): return "hi-IN-MadhurNeural" 
        elif re.search(r'\b(लडकी|औरत|रही)\b', text): return "hi-IN-SwaraNeural" 
        else: return "hi-IN-MadhurNeural" 
        
    else: 
        if re.search(r'\b(girl|woman|she|her)\b', text): return "en-US-AriaNeural" 
        elif re.search(r'\b(boy|man|he|him)\b', text): return "en-US-GuyNeural" 
        else: return "en-US-ChristopherNeural"

async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 1-Click Execution ---
if st.button("🚀 Generate Unlimited MP4 Video"):
    if script_text and char_prompt and action_details:
        with st.spinner("Raman AI STUDIO तुमची मास्टरपीस तयार करत आहे..."):
            try:
                voice_model = auto_detect_voice(script_text, language)
                st.info(f"🎙️ AI ने स्क्रिप्ट वाचून हा आवाज निवडला: **{voice_model}**")
                
                audio_path = "raman_voice.mp3"
                asyncio.run(generate_audio(script_text, voice_model, audio_path))
                audio_clip = AudioFileClip(audio_path)
                
                image_query = f"{char_prompt}, {action_details}, 32k resolution, highly detailed cinematic shot"
                encoded_query = urllib.parse.quote(image_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                
                img_data = requests.get(image_url).content
                image_path = "raman_frame.jpg"
                with open(image_path, "wb") as f:
                    f.write(img_data)
                
                st.info("🎬 MP4 व्हिडिओ रेंडर होत आहे...")
                img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                
                moving_clip = img_clip.resize(lambda t: 1 + 0.015 * t)
                w, h = img_clip.size
                moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                
                final_video = moving_clip.set_audio(audio_clip)
                output_video = "Raman_AI_Studio_Final.mp4"
                
                final_video.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा फायनल व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                audio_clip.close()
                final_video.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("कृपया सर्व रकाने भरा.")
