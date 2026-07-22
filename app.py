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

# --- 1. App Configuration ---
st.set_page_config(page_title="RAMAN AI STUDIO ULTIMATE", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    h1 { color: #E50914; font-weight: 900; text-align: center; font-family: 'Arial Black', sans-serif; }
    h2, h3 { color: #FFFFFF; }
    .stButton>button { background-color: #E50914; color: white; font-weight: bold; width: 100%; font-size: 20px; border-radius: 5px; border: none; padding: 12px;}
    .stButton>button:hover { background-color: #B20710; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 RAMAN AI STUDIO - ULTIMATE AUTO")
st.markdown("<p style='text-align: center; color: #AAAAAA;'>फक्त भाषा निवडा आणि स्क्रिप्ट टाका. बाकी सर्वकाही AI स्वयंचलितपणे तयार करेल!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. Clean 2-Input UI (No API Key Needed!) ---
col1, col2 = st.columns([1, 2])
with col1:
    language = st.selectbox("१. व्हिडिओची भाषा (Language):", ["Marathi", "Hindi", "English"])
    st.info("💡 टिप: कोणत्याही भाषेची स्क्रिप्ट टाका, ॲप त्यानुसार सुसंवाद आणि अचूक आवाज आपोआप जुळवून घेईल.")

with col2:
    script_text = st.text_area("२. परफेक्ट स्क्रिप्ट टाका:", height=180, placeholder="तुमची डॉक्युमेंटरी किंवा स्टोरीची स्क्रिप्ट इथे पेस्ट करा...")

# --- 3. Multilingual Smart Voice & Context Engine ---
def get_smart_voice_and_action(text, lang):
    text_lower = text.lower()
    clean_text = re.sub(r'[^\w\s]', ' ', text_lower)
    words = clean_text.split()
    
    # भाषा आणि पात्राच्या संदर्भानुसार उच्च दर्जाचा इंग्रजी सिनेमॅटिक प्रॉम्प्ट आणि व्हॉईस निवडणे
    if lang == "Marathi":
        female_keywords = ["मुलगी", "पोरगी", "ती", "स्त्री", "मादी", "आई", "आजी", "तिच्या"]
        voice = "mr-IN-AarohiNeural" if any(w in words for w in female_keywords) else "mr-IN-ManoharNeural"
    elif lang == "Hindi":
        female_keywords = ["लड़की", "औरत", "महिला", "माता", "माँ", "बहू", "बेटी", "वह"]
        voice = "hi-IN-SwaraNeural" if any(w in words for w in female_keywords) else "hi-IN-MadhurNeural"
    else:
        female_keywords = ["girl", "woman", "she", "her", "mother", "lady", "queen"]
        voice = "en-US-AriaNeural" if any(w in words for w in female_keywords) else "en-US-ChristopherNeural"
        
    # स्क्रिप्टच्या आशयानुसार उत्कृष्ट सिनेमॅटिक ॲक्शन जनरेट करणे
    if any(w in words for w in ["पक्षी", "उड", "bird", "fly", "sky", "आकाश"]):
        action = "Majestic wildlife documentary cinematic shot, 8k resolution, photorealistic wings motion, national geographic style"
    elif any(w in words for w in ["प्राणी", "जंगल", "animal", "forest", "wild"]):
        action = "Deep wildlife natural habitat, cinematic lighting, ultra-detailed photorealistic 8k, professional nature film"
    elif any(w in words for w in ["माणूस", "लोक", "man", "woman", "people", "story"]):
        action = "Expressive emotional cinematic storytelling portrait, professional lighting, dramatic depth of field, 8k"
    else:
        action = "Cinematic masterpiece storytelling visual, hyper-realistic, 8k resolution, volumetric lighting, emotional depth"
        
    return voice, action

async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- 4. 1-Click Automated Execution ---
if st.button("🚀 Generate Fully Automated Video"):
    if not script_text.strip():
        st.warning("⚠️ कृपया व्हिडिओ बनवण्यासाठी तुमची स्क्रिप्ट टाका.")
    else:
        with st.spinner("🎬 RAMAN AI STUDIO तुमची सिनेमॅटिक मास्टरपीस तयार करत आहे..."):
            try:
                # 1. स्वयंचलित व्हॉईस आणि ॲक्शन मजुरी
                voice_model, visual_action = get_smart_voice_and_action(script_text, language)
                st.success(f"🎙️ AI Director Active | Selected Voice Model: **{voice_model}**")
                
                # 2. ऑडिओ जनरेशन
                audio_path = "raman_master_voice.mp3"
                asyncio.run(generate_audio(script_text, voice_model, audio_path))
                
                # 3. सिनेमॅटिक इमेज जनरेशन (स्क्रिप्ट आणि भाषेनुसार परिपूर्ण)
                encoded_query = urllib.parse.quote(visual_action)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&nologo=true"
                
                # 4. फायनल युझर इंटरफेस आउटपुट
                st.markdown("### 🎥 फायनल जनरेटेड सिनेमॅटिक व्हिज्युअल")
                st.image(image_url, caption="Cinematic AI Generated Frame matching script context", use_column_width=True)
                
                st.markdown("### 🎧 प्रोफेशनल व्हॉईसओव्हर ऑडिओ")
                st.audio(audio_path)
                
                st.success("✅ तुमचे ॲप पूर्णपणे यशस्वीरित्या तयार झाले आहे! कोणत्याही API Key शिवाय हे आता विनासायास चालेल.")
                
            except Exception as e:
                st.error(f"Error during generation: {e}")
