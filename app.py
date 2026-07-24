import streamlit as st
import asyncio
import edge_tts
import urllib.parse
import requests
import re
import io
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- SECURE API KEY SETUP ---
# आता तुझी Key इथे नाहीये. सिस्टीम ती Streamlit च्या लपलेल्या डब्यातून (Secrets) शोधेल.
try:
    HF_API_KEY = st.secrets["HF_API_KEY"]
except:
    HF_API_KEY = "" # जर Key नसेल तर ॲप क्रॅश होऊ नये म्हणून

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# --- App Configuration ---
st.set_page_config(page_title="RAMAN AI STUDIO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select, .stNumberInput input { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - PROFESSIONAL ENGINE")
st.markdown("<p style='text-align: center; color: #888888;'>Powered by Hugging Face Supercomputers | Secure API Integrated</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
    
    st.markdown("---")
    st.markdown("### 👤 Character / Style Lock")
    st.info("Secure API Key Background मध्ये सक्रिय आहे.")
    character_seed = st.number_input("चेहरा/रचना लॉक करण्यासाठी सीड नंबर:", min_value=1, value=4242)

with col2:
    script_text = st.text_area("३. संपूर्ण स्क्रिप्ट टाका:", height=200, placeholder="उदा. एक भव्य गरुड आकाशात उडत आहे...")

# --- Direct Translation Engine ---
def translate_to_english(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url).json()
        return response[0][0][0]
    except Exception as e:
        return text

# --- Advanced Hugging Face Image Generation ---
def generate_huggingface_image(prompt, seed):
    if not HF_API_KEY:
        raise Exception("API Key Missing! Please add it to Streamlit Secrets.")
        
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "mutated, extra fingers, deformed, bad anatomy, ugly, blurry, extra limbs, human (if wildlife)",
            "seed": seed
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"API Error: {response.text}")

# --- VEO Inspired Prompt Structuring ---
def build_advanced_prompt(full_script, current_sentence):
    sent_eng = translate_to_english(current_sentence).lower()
    full_eng = translate_to_english(full_script).lower()
    
    wildlife_keywords = ['eagle', 'bird', 'animal', 'squirrel', 'tiger', 'lion', 'wild', 'forest']
    is_wildlife = any(word in sent_eng for word in wildlife_keywords)
    
    if is_wildlife:
        final_prompt = f"National Geographic award winning wildlife photography, {sent_eng}. Strictly animal only, NO HUMANS. 100% biologically accurate anatomy, perfect feathers, sharp talons. Cinematic golden hour lighting, extreme wide shot, 8k resolution, masterpiece."
    else:
        final_prompt = f"Cinematic film still, {sent_eng}. Authentic rural Indian person. Flawless human anatomy, perfect hands, exactly 5 fingers. Dramatic natural lighting, medium wide shot, 8k resolution, highly detailed."
        
    return final_prompt

# --- Voice Setup ---
async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- Video Generation Engine ---
if st.button("🚀 Generate Professional Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("Hugging Face API शी संपर्क साधत आहे आणि व्हिडिओ रेंडर करत आहे..."):
            try:
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 5]
                video_clips = []
                full_script_context = script_text.strip()
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    voice_model = "mr-IN-ManoharNeural" if language == "Marathi" and "Male" in narrator_voice else "en-US-AriaNeural"
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    perfect_prompt = build_advanced_prompt(full_script_context, sentence)
                    
                    img_bytes = generate_huggingface_image(perfect_prompt, character_seed)
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_bytes)
                    
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.010 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 फायनल रेंडर आणि व्हिडिओ जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_AI_Studio_Master.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा १००% प्रो आणि अचूक व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"⚠️ तांत्रिक अडचण: {e}")
