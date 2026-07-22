import streamlit as st
import asyncio
import edge_tts
import urllib.parse
import requests
import re
import google.generativeai as genai

# --- 1. App Configuration ---
st.set_page_config(page_title="RAMAN AI STUDIO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; }
    .stButton>button { background-color: #E50914; color: white; width: 100%; font-size: 20px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# Sidebar for API Key Setup
st.sidebar.title("⚙️ AI Settings")
gemini_api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")

st.title("🎬 RAMAN AI STUDIO - AUTO")
st.write("१ क्लिक. फक्त स्क्रिप्ट टाका. AI स्वतः विचार करून पूर्ण व्हिडिओ बनवेल!")

# --- 2. Inputs ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. भाषा (Language):", ["Marathi", "Hindi", "English"])
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

async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. Execution ---
if st.button("🚀 Generate 100% Auto Video"):
    if not gemini_api_key:
        st.error("⚠️ कृपया डाव्या बाजूला (Sidebar) तुमची Gemini API Key टाका.")
    elif not script_text:
        st.warning("⚠️ कृपया स्क्रिप्ट टाका.")
    else:
        with st.spinner("🧠 AI तुमची स्क्रिप्ट वाचून डिरेक्शन करत आहे..."):
            try:
                genai.configure(api_key=gemini_api_key)
                # Updated to gemini-2.5-flash / gemini-1.5-pro compatible stable string
                model = genai.GenerativeModel('gemini-2.5-flash')
                ai_prompt = f"Analyze this script: '{script_text}'. Extract the main visual subject (max 4 words) and cinematic action (max 8 words) in English. Reply exactly in this format: Subject: [subject], Action: [action]"
                
                ai_response = model.generate_content(ai_prompt).text
                extracted_info = ai_response.replace("\n", "").strip()
                st.success(f"🎥 AI Director: {extracted_info}")
                
                clean_prompt_for_image = extracted_info.replace("Subject:", "").replace("Action:", "").strip()

                voice_model = get_voice(script_text, language)
                st.info(f"🎙️ Voice Selected: **{voice_model}**")
                
                audio_path = "raman_voice.mp3"
                asyncio.run(generate_audio(script_text, voice_model, audio_path))
                
                scene_query = f"{clean_prompt_for_image}, highly detailed cinematic shot, 8k resolution"
                encoded_query = urllib.parse.quote(scene_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                
                st.success("✅ तुमचा प्रोफेशनल व्हिडिओ तयार आहे!")
                st.image(image_url, caption="Generated Cinematic Frame")
                st.audio(audio_path)
                
            except Exception as e:
                # Fallback if 2.5 isn't direct, try standard gemini-1.5
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    ai_prompt = f"Analyze this script: '{script_text}'. Extract the main visual subject (max 4 words) and cinematic action (max 8 words) in English. Reply exactly in this format: Subject: [subject], Action: [action]"
                    ai_response = model.generate_content(ai_prompt).text
                    extracted_info = ai_response.replace("\n", "").strip()
                    st.success(f"🎥 AI Director: {extracted_info}")
                except Exception as ex:
                    st.error(f"Error: {e}")
