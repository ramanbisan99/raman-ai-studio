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
st.set_page_config(page_title="RAMAN AI STUDIO - 100% AUTO PROFESSIONAL", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 8px; border: none; padding: 14px;}
    .stButton>button:hover { background-color: #B20710; }
    .stTextArea textarea, .stSelectbox select { background-color: #111111; color: #FFFFFF; border: 1px solid #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - 100% AUTO PROFESSIONAL")
st.markdown("<p style='text-align: center; color: #888888;'>Metaphor Scrubber: 100% ऑटोमॅटिक विषय ओळखणारा आणि मानवी चुका टाळणारा AI!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Setup ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. स्क्रिप्टची भाषा:", ["Marathi", "Hindi", "English"])
    narrator_voice = st.selectbox("२. निवेदकाचा आवाज:", ["Male (पुरुष)", "Female (स्त्री)"])
with col2:
    script_text = st.text_area("३. संपूर्ण स्क्रिप्ट टाका (उदा. गरुडाला पक्ष्यांचा राजा मानले जाते...):", height=250)

# --- 100% AUTOMATIC SUPER BRAIN (THE METAPHOR SCRUBBER) ---
def auto_perfect_prompt(full_script, current_sentence):
    try:
        system_instruction = f"""You are an elite cinematic AI prompt engineer for wildlife and human documentaries.
        Read the ENTIRE STORY for context: "{full_script}".
        Now, rewrite ONLY this sentence into a flawless image generation prompt: "{current_sentence}".
        
        CRITICAL AND MANDATORY RULES:
        1. METAPHOR SCRUBBING: If the story is about a bird/animal, and the text uses words like "King", "Queen", "Ruler", "He", "She", YOU MUST REMOVE THEM. Replace "King of birds" with "Apex predator bird". NEVER use the word "King" for an animal.
        2. ANIMAL/NATURE CONTEXT: If the subject is wildlife (e.g., Eagle), append EXACTLY: "ONLY the animal in its natural habitat. ABSOLUTELY NO HUMANS, NO HUMAN KINGS, NO CLOTHING, NO CROWNS."
        3. HUMAN CONTEXT: If the story is actually about humans, append: "Authentic rural dark-haired Indian person with brown skin."
        4. CAMERA & QUALITY: Append to ALL prompts: "Extreme wide angle shot, taken from a far distance, FULL BODY completely visible, real-world physics, perfect anatomical geometry, 32K resolution, National Geographic photography style."
        
        Output ONLY the final locked English prompt. Do not add any conversational text.
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
if st.button("🚀 Generate 100% Auto Perfect Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("AI चा ऑटोमॅटिक मेंदू स्क्रिप्टमधील उपमा (Metaphors) काढून 100% अचूक दृश्य बनवत आहे..."):
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
                    
                    # 100% Auto Brain Logic with Metaphor Scrubbing
                    perfect_prompt = auto_perfect_prompt(full_script_context, sentence)
                    st.caption(f"🧠 Auto-Brain Prompt: {perfect_prompt}")
                    
                    image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(perfect_prompt)}?width=1280&height=720&nologo=true"
                    img_data = requests.get(image_url).content
                    image_path = f"temp_frame_{i}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    # Smooth professional zoom
                    img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                    moving_clip = img_clip.resize(lambda t: 1 + 0.010 * t) 
                    w, h = img_clip.size
                    moving_clip = moving_clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
                    
                    final_scene = moving_clip.set_audio(audio_clip)
                    video_clips.append(final_scene)
                
                st.info("🔄 व्हिडिओची व्यावसायिक जोडणी सुरू आहे...")
                final_movie = concatenate_videoclips(video_clips, method="compose")
                output_video = "Raman_100_Auto_Professional.mp4"
                final_movie.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ तुमचा १००% ऑटोमॅटिक आणि अचूक व्हिडिओ तयार आहे!")
                st.video(output_video)
                
                final_movie.close()
                for clip in video_clips:
                    clip.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
