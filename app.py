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
st.set_page_config(page_title="RAMAN AI STUDIO - PROFESSIONAL MASTER", page_icon="🎬", layout="wide")

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
st.markdown("<p style='text-align: center; color: #888888;'>Global Context Memory: संपूर्ण स्क्रिप्ट लक्षात ठेवून 100% अचूक दृश्ये!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
with col2:
    script_text = st.text_area("३. संपूर्ण स्क्रिप्ट टाका:", height=200, placeholder="उदा. गरुड आकाशात उडतो. तो खूप वेगाने जातो...")

# --- 100% AUTOMATIC SUPER BRAIN (WITH CONTEXT) ---
def auto_perfect_prompt(full_script, current_sentence):
    try:
        # हा AI आता संपूर्ण स्क्रिप्ट वाचेल आणि मग ठरवेल की 'तो' म्हणजे कोण.
        system_instruction = f"""You are a master cinematic director. 
        Here is the FULL STORY for context: "{full_script}".
        
        Now, generate a highly detailed image generation prompt ONLY for this specific sentence: "{current_sentence}".
        
        CRITICAL RULES:
        1. RESOLVE PRONOUNS: Use the FULL STORY to understand who 'he', 'she', or 'it' is. If 'he' refers to an eagle, write 'The Bald Eagle' in the prompt. DO NOT generate a human if the story is about an animal.
        2. ANIMAL RULE: If the main subject of the story is an animal/bird, explicitly state: "ONLY the animal in its natural habitat, ABSOLUTELY NO HUMANS in the frame."
        3. HUMAN RULE: If the subject is a human, explicitly state: "Authentic dark-haired Indian person."
        4. REMOVE METAPHORS: Translate poetic words into literal physical actions.
        5. QUALITY: Always end the prompt with: "Extreme wide angle, taken from a far distance, full body completely visible, flawless real-world physics, exact anatomical geometry, 32K resolution, highly detailed cinematic documentary style."
        
        Output ONLY the final English prompt, nothing else.
        """
        
        url = f"https://text.pollinations.ai/{urllib.parse.quote(system_instruction)}"
        response = requests.get(url)
        
        if response.status_code == 200 and "error" not in response.text.lower():
            return response.text.strip()
        else:
            return current_sentence
    except Exception as e:
        return current_sentence

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
if st.button("🚀 Generate 100% Professional Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("AI संपूर्ण स्क्रिप्टचा संदर्भ (Context) समजून अचूक दृश्ये बनवत आहे..."):
            try:
                # 10 अक्षरांपेक्षा मोठी वाक्येच घेणे (फालतू कट टाळण्यासाठी)
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 10]
                
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
                    
                    # Passing FULL SCRIPT to resolve pronouns like "He/It" correctly
                    perfect_prompt = auto_perfect_prompt(full_script_context, sentence)
                    st.caption(f"🧠 Context Brain Prompt: {perfect_prompt}")
                    
                    image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(perfect_prompt)}?width=1280&height=720&nologo=true"
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    # अत्यंत स्मूथ आणि प्रोफेशनल झूम
                    moving_clip = img_clip.resize(lambda t: 1 + 0.008 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 व्हिडिओची व्यावसायिक जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_Professional_Master.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा परिपूर्ण व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
