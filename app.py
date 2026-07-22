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
st.markdown("<p style='text-align: center; color: #888888;'>१ क्लिक. डायनॅमिक ॲक्शन, अचूक दृश्ये आणि १००% स्वयंचलित!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. 100% Automated UI ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा (Language):", ["Marathi", "Hindi", "English"])
    st.success("🤖 **32K Dynamic Brain Active:** हा मोड प्रत्येक वाक्यातील 'ॲक्शन' आणि 'पात्र' ओळखून अचूक डायनॅमिक दृश्य तयार करेल.")
with col2:
    script_text = st.text_area("२. परफेक्ट स्क्रिप्ट टाका:", height=200, placeholder="तुमची स्क्रिप्ट इथे पेस्ट करा. (उदा. एक गरुड आकाशात वेगाने उडत होते. नंतर ते एका झाडावर शांत बसले.)")

# --- 3. Dynamic Voice Detection ---
def get_voice_for_scene(sentence, lang):
    s_lower = sentence.lower()
    # स्त्री किंवा मुलीचा संदर्भ असल्यास फिमेल व्हॉईस, अन्यथा मेल व्हॉईस
    female_words = ["स्त्री", "मुलगी", "आई", "ती", "woman", "girl", "she", "her", "राणी", "म्हातारी", "आजी"]
    is_female = any(w in s_lower for w in female_words)
    
    if lang == "Marathi":
        return "mr-IN-AarohiNeural" if is_female else "mr-IN-ManoharNeural"
    elif lang == "Hindi":
        return "hi-IN-SwaraNeural" if is_female else "hi-IN-MadhurNeural"
    else:
        return "en-US-AriaNeural" if is_female else "en-US-ChristopherNeural"

async def generate_audio_segment(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 32K Video Generation Engine ---
if st.button("🚀 Generate 32K Perfect Action Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("🧠 AI तुमचा '32K Master Prompt' आणि 'ॲक्शन' समजून दृश्ये बनवत आहे..."):
            try:
                # स्क्रिप्टला अचूक वाक्यांमध्ये तोडणे
                sentences = [s.strip() for s in re.split(r'[.?!|।]+', script_text) if len(s.strip()) > 3]
                
                if not sentences:
                    st.error("स्क्रिप्ट योग्य नाही. कृपया पूर्णविराम असलेली वाक्ये टाका.")
                    st.stop()
                
                video_clips = []
                
                # RAMAN'S 32K MASTER PROMPT TEMPLATE
                VISUAL_STYLE = "Create an ultra-high-definition, world-class, cinematic masterpiece video with absolute maximum quality and realism. The video must look like it was shot for a Hollywood documentary or National Geographic feature film. The visuals must be hyper-realistic, true-to-life, with extreme micro-details, zero artificial look, and flawless physical accuracy. Render the video in 32K ultra-resolution, HDR10+, full dynamic range, with perfect clarity in every single frame. Use cinematic lighting with physically accurate global illumination, realistic soft shadows, natural light scattering, deep contrast, and beautiful depth of field. All materials, skin, surfaces, water, metal, vegetation, and air must have photorealistic physics. Everything must be geographically correct to Maharashtra. Aspect Ratio: 16:9."
                CHAR_INSTRUCTION = "According to script context needed create a 100% accurate likeness of this person, human, animals, birds, insects, plants, objects, trees, snakes, fruits, or even abstract elements. The facial features, identity, body, and outfit must remain identical throughout. Hand movements and physical acting must completely match the action of the script. Strictly NO face morphing, age change, or identity drift. Any secondary elements dictated by the script must flawlessly match the script's visual context."
                
                for i, sentence in enumerate(sentences):
                    st.text(f"🎬 Scene {i+1} रेंडर होत आहे: '{sentence[:30]}...'")
                    
                    # 1. ऑडिओ (वाक्यानुसार आवाज सेट करणे)
                    voice_model = get_voice_for_scene(sentence, language)
                    audio_path = f"temp_audio_{i}.mp3"
                    asyncio.run(generate_audio_segment(sentence, voice_model, audio_path))
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 2. ॲक्शन इमेज (Dynamic Action Prompting with 32K Master Prompt)
                    scene_action = f"Detailed English Scene Description and Flawless Physical Acting/Gestures taking place right now: '{sentence}'. Capture this exact action perfectly in motion without text."
                    final_image_prompt = f"{VISUAL_STYLE} {CHAR_INSTRUCTION} {scene_action}"
                    
                    encoded_query = urllib.parse.quote(final_image_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                    
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # 3. सिनेमॅटिक मोशन (Ken Burns Zoom)
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.015 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 सर्व सीन्सची व्यावसायिक जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                
                output_video = "Raman_Ultimate_32K_Action.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा डायनॅमिक ॲक्शन, परफेक्ट इमोशन्स आणि 32K दर्जाचा व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                # मेमरी क्लिनअप
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
