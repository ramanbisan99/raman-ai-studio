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
st.set_page_config(page_title="RAMAN AI STUDIO - FINAL DRAFT BUILDER", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - FINAL DRAFT BUILDER")
st.markdown("<p style='text-align: center; color: #888888;'>Hardcoded Python Scanner: 100% ऑटोमॅटिक विषय ओळख (Drafting Tool)</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
with col2:
    script_text = st.text_area("३. संपूर्ण स्क्रिप्ट टाका:", height=250, placeholder="उदा. एक गरुड आकाशात उंच उडत आहे...")

# --- Direct Translation Engine ---
def translate_to_english(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url).json()
        return response[0][0][0]
    except Exception as e:
        return text

# --- 100% DETERMINISTIC PYTHON BRAIN (WITH ANATOMY FIX) ---
def generate_perfect_prompt(full_script, current_sentence):
    full_eng = translate_to_english(full_script).lower()
    sent_eng = translate_to_english(current_sentence).lower()
    
    wildlife_keywords = ['eagle', 'bird', 'animal', 'tiger', 'lion', 'wild', 'forest', 'vulture', 'nature']
    is_wildlife = any(word in full_eng for word in wildlife_keywords)
    
    if is_wildlife:
        bad_words_pattern = re.compile(r'\b(king|queen|ruler|he|she|his|her|man|person|human)\b', re.IGNORECASE)
        safe_sentence = bad_words_pattern.sub('the majestic bird', sent_eng)
        
        final_prompt = f"Action: {safe_sentence}. STRICT RULES: ONLY show the animal/bird in its natural habitat. ABSOLUTELY NO HUMANS, NO PEOPLE. 100% ANATOMICALLY CORRECT, perfect feather structure, normal legs. Extreme wide shot, taken from a far distance, FULL BODY visible, 32K resolution, award-winning National Geographic wildlife photography."
    else:
        final_prompt = f"Action: {sent_eng}. STRICT RULES: Authentic rural dark-haired Indian person with brown skin. Extreme wide angle shot, taken from a far distance, FULL BODY completely visible. Flawless real-world physics, perfect anatomical geometry, 32K resolution, highly detailed cinematic style."
        
    return final_prompt

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
if st.button("🚀 Generate Perfect Draft Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("AI 100% अचूक प्रॉम्ट बनवत आहे..."):
            try:
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 5]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही.")
                    st.stop()
                
                video_clips = []
                full_script_context = script_text.strip()
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    voice_model = get_voice_model(language, narrator_voice)
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    perfect_prompt = generate_perfect_prompt(full_script_context, sentence)
                    st.caption(f"⚙️ Locked Python Prompt: {perfect_prompt}")
                    
                    image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(perfect_prompt)}?width=1280&height=720&nologo=true"
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.010 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 व्हिडिओची जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_Final_Draft_Video.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा फायनल ड्राफ्ट व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
