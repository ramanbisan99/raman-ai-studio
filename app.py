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
st.set_page_config(page_title="RAMAN AI STUDIO - SMART LANGUAGE PRO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - SMART LANGUAGE PRO")
st.markdown("<p style='text-align: center; color: #888888;'>रोमन मराठी (Ha garud...) ऑटोमॅटिक समजणारा प्रगत मेंदू आणि अचूक वास्तव!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
with col2:
    script_text = st.text_area("३. स्क्रिप्ट टाका (रोमन मराठी जसे 'Ha garud...' इथे चालेल!):", height=200)

# --- 100% SMART LLM Translation Engine ---
def translate_to_english(text):
    try:
        # हा नवीन AI मेंदू रोमन मराठी (Minglish) अतिशय अचूक ओळखतो.
        prompt = f"Translate the following Marathi or Romanized Marathi text to plain English. Only output the English translation. Text: {text}"
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        response = requests.get(url)
        
        if response.status_code == 200 and "error" not in response.text.lower():
            return response.text.strip()
        else:
            # Fallback to Google if the above fails
            google_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
            res = requests.get(google_url).json()
            return res[0][0][0]
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
if st.button("🚀 Generate Perfect Smart Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("AI तुमची रोमन मराठी भाषा समजून घेत आहे आणि 32K अचूक दृश्य बनवत आहे..."):
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
                    
                    # 2. Smart LLM Translation (Understands "Ha garud...")
                    translated_text = translate_to_english(sentence)
                    
                    # 3. CONTEXT PERFECT PROMPT
                    # हा प्रॉम्ट सक्ती करतो की प्राणी असेल तर फक्त प्राणीच दाखवा, माणूस नको.
                    final_image_prompt = f"Subject: {translated_text}. CRITICAL RULE: Generate exactly what is described. If it is an animal/bird, show ONLY the animal in its natural habitat with perfectly accurate anatomy. Do NOT include any humans unless explicitly mentioned. Cinematic wide angle, Full Body visible, 100% flawless real-world physics, photorealistic, 32k resolution, National Geographic documentary masterclass."
                    
                    st.caption(f"⚙️ Auto-Prompt: {final_image_prompt}")
                    
                    # 4. Image Generation
                    image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_image_prompt)}?width=1280&height=720&nologo=true"
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 5. Motion
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.012 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                # 6. Final Assembly
                st.info("🔄 व्हिडिओ जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_Smart_Language_Master.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा स्मार्ट आणि अचूक व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
