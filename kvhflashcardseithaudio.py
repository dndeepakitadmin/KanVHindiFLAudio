import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os

# For live microphone input
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

st.set_page_config(page_title="Hindi to Kannada Learning", layout="centered")
st.title("📝 Learn Kannada using Hindi script")
st.subheader("Type, Upload Audio, or Speak in Hindi to Learn Kannada")

# ---------- Function to generate audio ----------
def generate_audio_kannada(kannada_text):
    tts = gTTS(text=kannada_text, lang="kn")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# ---------- Input Method Selection ----------
input_method = st.radio("Select Input Method:", ["Type Hindi Text", "Upload Hindi Audio", "Speak Live"])

text = ""

# ---------- 1. Typed Input ----------
if input_method == "Type Hindi Text":
    text = st.text_area("Enter Hindi text here (e.g., आप कैसे हैं?)", height=120)

# ---------- 2. Upload Audio ----------
elif input_method == "Upload Hindi Audio":
    audio_file = st.file_uploader("Upload Hindi Audio (mp3/wav)", type=["mp3","wav"])
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            if audio_file.name.endswith(".mp3"):
                sound = AudioSegment.from_file(audio_file)
                sound.export(tmp_file.name, format="wav")
                audio_path = tmp_file.name
            else:
                audio_path = tmp_file.name
                audio_file.seek(0)
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
        # Speech Recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="hi-IN")
                st.success(f"Detected Hindi Text: {text}")
            except Exception as e:
                st.error(f"Could not recognize audio: {e}")

# ---------- 3. Live Microphone Input ----------
elif input_method == "Speak Live":
    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.audio_data = None

        def recv_audio(self, frame):
            self.audio_data = frame.to_ndarray()
            return frame

    st.info("Click 'Start' to speak in Hindi and press 'Translate' when done.")
    ctx = webrtc_streamer(key="live-audio", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor)

# ---------- Single Translate Button ----------
translate_clicked = st.button("Translate")

if translate_clicked:
    if text.strip():
        try:
            # ---------- Sentence Translation ----------
            kannada = GoogleTranslator(source="hi", target="kn").translate(text)
            kannada_english = transliterate(kannada, sanscript.KANNADA, sanscript.ITRANS)
            kannada_in_hindi = process('Kannada', 'Devanagari', kannada)

            # ---------- Display Sentence Outputs ----------
            st.markdown("### 🔹 Translation Results")
            st.markdown(f"**Hindi Input:**  \n:blue[{text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada}]")
            st.markdown(f"**Kannada in Hindi letters:**  \n:orange[{kannada_in_hindi}]")
            st.markdown(f"**Kannada in English phonetics:**  \n`{kannada_english}`")

            # Sentence audio
            sentence_audio_file = generate_audio_kannada(kannada)
            st.audio(sentence_audio_file)

            # ---------- Flashcards ----------
            st.markdown("### 🎴 Flashcards for Each Word")
            words = text.strip().split()
            for word in words:
                try:
                    kannada_word = GoogleTranslator(source="hi", target="kn").translate(word)
                    kannada_in_hindi_word = process('Kannada', 'Devanagari', kannada_word)
                    kannada_phonetic = transliterate(kannada_word, sanscript.KANNADA, sanscript.ITRANS)

                    with st.expander(f"Flashcard: {word}"):
                        st.markdown(f"**Hindi:** {word}")
                        st.markdown(f"**Kannada:** {kannada_word}")
                        st.markdown(f"**Kannada in Hindi letters:** {kannada_in_hindi_word}")
                        st.markdown(f"**Phonetic (English):** `{kannada_phonetic}`")
                        
                        # Flashcard audio
                        word_audio_file = generate_audio_kannada(kannada_word)
                        st.audio(word_audio_file)

                except Exception as e:
                    st.warning(f"Cannot translate the word: {word}")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please type, upload, or speak some Hindi input!")
