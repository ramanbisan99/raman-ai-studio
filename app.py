# --- Error Patch for MoviePy ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# --- Main App Code ---
import streamlit as st
import asyncio
import edge_tts
import urllib.parse
import requests
import re
import os
import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- 1. App Configuration ---
st.set_page_config(page_title="Raman AI STUDIO - AUTO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; }
    .stButton>button { background-color: #E50914; color: white; width: 100%; font-size: 20px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# Sidebar for API Key Setup
st.sidebar.title("⚙️ AI Settings")
gemini_api_key = st.sidebar.text_input("Gemini API Key टाका (Free):", type="password")
st.sidebar.markdown("*(API Key नसेल तर [इथे क्लिक करून फ्री मध्ये मिळवा](https://aistudio.google.com/app/apikey))*")

st.title("🎬 RAMAN AI STUDIO - AUTO")
st.write("१ क्लिक. फक्त स्क्रिप्ट टाका. AI स्वतः विचार करून पूर्ण व्हिडिओ बनवेल!")

# --- 2. Inputs (Now Only 2 Things Needed!) ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. व्हिडिओची भाषा (Language):", ["Marathi", "Hindi", "English"])
with col2:
    script_text = st.text_area("२. तुमची स्क्रिप्ट इथे टाका:", height=150, placeholder="उदा. एक गरुड आकाशात उडत होता...")

# --- 3. Smart Voice Engine ---
def get_voice(text, lang):
    text = text.lower()
    clean_text = re.sub(r'[^\w\s]', ' ', text)
    words = clean_text.split()
    
    if lang == "Marathi":
        return "mr-IN-AarohiNeural" if any(w in words for w in ["मुलगी", "पोरगी", "ती", "स्त्री", "मादी", "तिच्या"]) else "mr-IN-ManoharNeural"
    elif lang == "Hindi":
        return "hi-IN-SwaraNeural" if any(w in words for w in ["लडकी", "औरत", "रही", "वह", "उसकी"]) else "hi-IN-MadhurNeural"
    else:
        return "en-US-AriaNeural" if any(w in words for w in ["girl", "woman", "she", "her"]) else "en-US-ChristopherNeural"

async def generate_audio_segment(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 1-Click Fully Auto Execution ---
if st.button("🚀 Generate 100% Auto Video"):
    if not gemini_api_key:
        st.error("⚠️ कृपया डाव्या बाजूला (Sidebar) तुमची Gemini API Key टाका.")
    elif not script_text:
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("🧠 AI तुमची स्क्रिप्ट वाचून डिरेक्शन ठरवत आहे..."):
            try:
                # 1. Gemini AI Analysis (The Brain)
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                ai_prompt = f"Analyze this script: '{script_text}'. Extract the main visual subject (max 4 words) and cinematic action (max 8 words) in English. Reply exactly in this format: Subject: [subject], Action: [action]"
                
                ai_response = model.generate_content(ai_prompt).text
                extracted_info = ai_response.replace("\n", "").strip()
                st.success(f"🎥 AI Director Decision: {extracted_info}")
                
                # Extract for image prompt
                clean_prompt_for_image = extracted_info.replace("Subject:", "").replace("Action:", "").strip()

                # 2. Scene Division
                sentences = re.split(r'(?<=[।|!|\.|\?])\s+', script_text.strip())
                sentences = [s for s in sentences if len(s) > 3]
                
                voice_model = get_voice(script_text, language)
                st.info(f"🎙️ Voice Selected: **{voice_model}** | Total Scenes: **{len(sentences)}**")
                
                video_clips = []
                
                # 3. Generating Scenes
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे...")
                    
                    audio_path = f"audio_{i}.mp3"
                    asyncio.run(generate_audio_segment(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Generate Image using AI Brain's prompt
                    scene_query = f"{clean_prompt_for_image}, highly detailed cinematic shot, part {i+1}"
                    encoded_query = urllib.parse.quote(scene_query)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                    
                    img_data = requests.get(image_url).content
                    image_path = f"frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # Stitch Video
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.015 * t)
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    final_clip = moving_clip.set_audio(audio_clip)
                    
                    video_clips.append(final_clip)
                
                # 4. Final Compile
                st.info("🔄 सर्व सीन्स एकत्र जोडत आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_AI_Auto_Final.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा 100% ऑटोमॅटिक व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                # Cleanup
                final_movie.close()
                for clip in video_clips: clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
