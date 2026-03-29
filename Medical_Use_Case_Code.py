import streamlit as st
import openai
import fitz
import requests
from io import BytesIO
from PIL import Image
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import re

st.set_page_config(page_title="💊 Prescription Voice Assistant",
                   layout="centered")
st.title("💊 Prescription Reader & Narrator")
# Inputs
openai_api = st.text_input("🔐 OpenAI API Key", type="password")
input_type = st.radio("Choose input method:", ["📄 Upload PDF", "📸
                                               Camera"])
                                               user_lang = st.text_input("🌐 Translate to Language (e.g. en, hi, kn)",
                                                                         value="en")
image_bytes = None
# PDF Upload
if input_type == "📄 Upload PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_pdf:
    pdf_doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
f
irst_page = pdf_doc.load_page(0)
pix = first_page.get_pixmap()
image_bytes = pix.tobytes("jpeg")
st.image(image_bytes, caption="Extracted from PDF",
         use_column_width=True)

# Camera Input
elif input_type == "📸 Camera":
camera_input = st.camera_input("Take a photo of medicine strip")
if camera_input:
    image_bytes = camera_input.read()
st.image(image_bytes, caption="Captured Image",
         use_column_width=True)

# Convert image to base64


def prepare_image_for_vision(image_bytes):
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


# GPT-4 Vision Query (focus only on prescription)
def query_prescription_only(image_data_url):
    openai.api_key = openai_api
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": [
                                            {"type": "text", "text": "Extract only the prescription details from this
                                             medicine image, including tablet name, usage, dosage, and instructions.
                                        Format it as a
    short
    summary
    for elderly users, like a nurse speaking politely."},
    {"type": "image_url", "image_url": {"url": image_data_url}}
    ]}
    ],
    max_tokens = 800
    )
    return response.choices[0].message.content.strip()


# Clean audio text
def clean_audio_text(text):
    text = re.sub(r'[^\w\s.,]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return f"Hello! {text}"


# Convert text to speech
def speak(text, lang):
    cleaned = clean_audio_text(text)
    tts = gTTS(text=cleaned, lang=lang)
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio


# Main processing
if image_bytes and openai_api:
    if st.button("🧠 Extract Prescription"):
        with st.spinner("Analyzing with GPT-4..."):
            img_url = prepare_image_for_vision(image_bytes)
            gpt_output = query_prescription_only(img_url)
            translated = GoogleTranslator(source="auto",
                                          target=user_lang).translate(gpt_output)

            st.markdown("### 📝 Prescription Summary")
            st.success(translated)

            st.markdown("### 🔈 Voice Output")
            audio = speak(translated, user_lang)
            st.audio(audio, format="audio/mp3")