import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="Hindi to Kannada Learning", layout="centered")

st.title("📝 Learn Kannada using Hindi script")
st.subheader("हिंदी अक्षरों का उपयोग करके कन्नड़ सीखें")

# Input
text = st.text_area("Enter Hindi text here (e.g., आप कैसे हैं?)", height=120)

def generate_audio_kannada(kannada_text):
    """Generate temporary mp3 file for given Kannada text"""
    tts = gTTS(text=kannada_text, lang="kn")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

if st.button("Translate"):
    if text.strip():
        try:
            # ---------------- Sentence Translation ---------------- #
            # Hindi → Kannada translation (whole sentence)
            kannada = GoogleTranslator(source="hi", target="kn").translate(text)

            # Kannada → English phonetics (IAST)
            kannada_english = transliterate(kannada, sanscript.KANNADA, sanscript.ITRANS)

            # Kannada → Hindi letters (transliteration)
            kannada_in_hindi = process('Kannada', 'Devanagari', kannada)

            # Display outputs
            st.markdown("### 🔹 Translation Results")
            st.markdown(f"**Hindi Input:**  \n:blue[{text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada}]")
            st.markdown(f"**Kannada in Hindi letters:**  \n:orange[{kannada_in_hindi}]")
            st.markdown(f"**Kannada in English phonetics:**  \n`{kannada_english}`")

            # Sentence audio
            sentence_audio_file = generate_audio_kannada(kannada)
            st.audio(sentence_audio_file)

            # ---------------- Flashcards ---------------- #
            st.markdown("### 🎴 Flashcards for Each Word")
            words = text.strip().split()
            for word in words:
                try:
                    kannada_word = GoogleTranslator(source="hi", target="kn").translate(word)
                    kannada_in_hindi_word = process('Kannada', 'Devanagari', kannada_word)
                    kannada_phonetic = transliterate(kannada_word, sanscript.KANNADA, sanscript.ITRANS)

                    # Expander for flashcard
                    with st.expander(f"Flashcard: {word}"):
                        st.markdown(f"**Hindi:** {word}")
                        st.markdown(f"**Kannada:** {kannada_word}")
                        st.markdown(f"**Kannada in Hindi letters:** {kannada_in_hindi_word}")
                        st.markdown(f"**Phonetic (English):** `{kannada_phonetic}`")

                        # Generate audio for the word
                        word_audio_file = generate_audio_kannada(kannada_word)
                        st.audio(word_audio_file)

                except Exception as e:
                    st.warning(f"Cannot translate the word: {word}")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter some Hindi text to translate!")

# ---------------- Cleanup: delete temporary audio files on exit ---------------- #
import atexit
def cleanup_temp_files():
    for file in os.listdir(tempfile.gettempdir()):
        if file.endswith(".mp3"):
            try:
                os.remove(os.path.join(tempfile.gettempdir(), file))
            except:
                pass

atexit.register(cleanup_temp_files)
