import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import streamlit as st
import asyncio
import edge_tts
import urllib.parse
import requests
import re
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- App Configuration ---
st.set_page_config(page_title="RAMAN AI STUDIO - THE CONTENT LAB PRO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - PROFESSIONAL MASTER")
st.markdown("<p style='text-align: center; color: #888888;'>Strict Wide-Angle, 100% Indian Characters, Full Body Distance Shots!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
with col2:
    script_text = st.text_area("३. स्क्रिप्ट टाका (रोमन किंवा देवनागरी):", height=200, placeholder="उदा. Mi shalet jat ahe...")

# --- ULTRA SMART LLM Translation & Formatting Engine ---
def smart_translate_and_format(text):
    try:
        # हा प्रॉम्ट आपोआप 'Indian', 'Wide Shot' आणि 'Full Body' सक्तीने जोडेल.
        system_prompt = f"""Translate this Marathi/Roman Marathi text to literal English for an image prompt. 
        CRITICAL RULES TO ENFORCE:
        1. If humans are mentioned, explicitly state 'Authentic dark-haired rural Indian person/people with Indian facial features and brown skin'.
        2. MANDATORY CAMERA ANGLE: Add 'Extreme wide shot taken from a far distance, full body completely visible from head to toe'.
        3. Remove ANY metaphors (e.g., 'like a snake'). 
        Output ONLY the final highly detailed English visual description. Text: {text}"""
        
        url = f"https://text.pollinations.ai/{urllib.parse.quote(system_prompt)}"
        response = requests.get(url)
        
        if response.status_code == 200 and "error" not in response.text.lower():
            return response.text.strip()
        else:
            return text
    except Exception as e:
        return text

# --- Voice Setup ---
def get_voice_model(lang, voice_type):
    if lang == "Marathi":
        return "mr-IN-AarohiNeural" if voice_type == "Female (स्त्री)" else "mr-IN-ManoharNeural"
    elif lang == "Hindi":
        return "hi-IN-SwaraNeural" if voice_type == "Female (स्त्री)" else "hi-IN-MadhurNeural"
    else:
        return "en-US-AriaNeural" if voice_type == "Female (स्त्री)" else "en-US-ChristopherNeural"

async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- Video Generation Engine ---
if st.button("🚀 Generate Perfect Automatic Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("AI तुमची स्क्रिप्ट वाचून लांबून घेतलेले भारतीय दृश्य बनवत आहे..."):
            try:
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही.")
                    st.stop()
                
                video_clips = []
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    voice_model = get_voice_model(language, narrator_voice)
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Smart Translation & Distance Formatting
                    smart_text = smart_translate_and_format(sentence)
                    
                    # FINAL GEOMETRY & PHYSICS PROMPT
                    final_image_prompt = f"Subject and Action: {smart_text}. MANDATORY ENFORCEMENT: Absolutely NO extreme close-ups of faces. Camera must be far away. 100% flawless real-world physics, perfect anatomical geometry, exact scale and proportions. Hyper-realistic environment. Zero mutations, zero text, zero logos. 32K resolution, highly detailed, professional cinematic documentary masterpiece."
                    
                    st.caption(f"⚙️ Auto-Prompt: {final_image_prompt}")
                    
                    image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_image_prompt)}?width=1280&height=720&nologo=true"
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.012 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 व्हिडिओ जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_The_Content_Lab_Final.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
