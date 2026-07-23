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
st.set_page_config(page_title="RAMAN AI STUDIO - FULL BODY ACTION", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - FULL BODY ACTION")
st.markdown("<p style='text-align: center; color: #888888;'>कोणतेही क्लोज-अप नाहीत! फक्त लांबून घेतलेले Full Body आणि Action शॉट्स.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
with col2:
    script_text = st.text_area("३. स्क्रिप्ट टाका:", height=200, placeholder="उदा. काळे गिधाड झाडावर बसले आहे...")

# --- Safe Translation Engine (Removes Metaphors) ---
def smart_translate(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url).json()
        translated = response[0][0][0]
        
        # सापासारखा (Snake-like) सारखे शब्द काढून टाकणे जेणेकरून चुका होणार नाहीत.
        translated = translated.replace("snake-like", "").replace("like a snake", "")
        return translated
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
if st.button("🚀 Generate Perfect Full Body Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("AI लांबून (Long Shot) कॅमेरा सेट करत आहे आणि दृश्य बनवत आहे..."):
            try:
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही.")
                    st.stop()
                
                video_clips = []
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    # 1. Audio
                    voice_model = get_voice_model(language, narrator_voice)
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 2. Translation
                    translated_text = smart_translate(sentence)
                    
                    # 3. STRICT CAMERA & FULL BODY PROMPT
                    # या प्रॉम्टमुळे AI चेहऱ्याजवळ कॅमेरा नेऊ शकणार नाही.
                    final_image_prompt = f"Subject and Action: {translated_text}. MANDATORY CAMERA RULES: Extreme wide shot, long shot taken from a distance. FULL BODY COMPLETELY VISIBLE from head to toe/tail. Show the entire subject in its surrounding environment. ABSOLUTELY NO CLOSE-UPS, NO PORTRAITS, NO MACRO SHOTS. 100% accurate true-to-life anatomy, natural habitat, real-world physics, photorealistic, 32k resolution, National Geographic documentary style."
                    
                    st.caption(f"⚙️ Auto-Prompt: {final_image_prompt}")
                    
                    # 4. Image Generation
                    image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_image_prompt)}?width=1280&height=720&nologo=true"
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 5. Motion (Subtle zoom)
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.012 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                # 6. Final Assembly
                st.info("🔄 व्हिडिओ जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_Full_Body_Reality.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
