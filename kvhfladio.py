import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process
from gtts import gTTS
import tempfile
import time

# ---------------------------
# 🌐 App Config
# ---------------------------
st.set_page_config(page_title="Hindi to Kannada Learning", layout="centered")
st.title("📝 Learn Kannada using Hindi Script")
st.subheader("Type Hindi text to Learn Kannada")

# ---------------------------
# 🎧 Audio Function
# ---------------------------
def generate_audio_kannada(kannada_text):
    """Generate audio pronunciation for Kannada text."""
    tts = gTTS(text=kannada_text, lang="kn")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# ---------------------------
# ⚡ Cached Translation Function
# ---------------------------
@st.cache_data(show_spinner=False)
def translate_sentence(text):
    """Translate Hindi → Kannada and return full results."""
    kannada = GoogleTranslator(source="hi", target="kn").translate(text)
    kannada_english = transliterate(kannada, sanscript.KANNADA, sanscript.ITRANS)
    kannada_in_hindi = process("Kannada", "Devanagari", kannada)
    return kannada, kannada_english, kannada_in_hindi

# ---------------------------
# 📝 Input
# ---------------------------
text = st.text_area("Enter Hindi text here (उदाहरण: आप कैसे हैं?)", height=120)
translate_clicked = st.button("Translate")

# ---------------------------
# 🚀 Main Logic
# ---------------------------
if translate_clicked:
    if text.strip():
        try:
            start = time.time()

            # Sentence-level translation
            kannada, kannada_english, kannada_in_hindi = translate_sentence(text)

            st.markdown("### 🔹 Translation Results")
            st.markdown(f"**Hindi Input:**  \n:blue[{text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada}]")
            st.markdown(f"**Kannada in Hindi Letters:**  \n:orange[{kannada_in_hindi}]")
            st.markdown(f"**Kannada in English Phonetics:**  \n`{kannada_english}`")

            # Sentence-level audio
            sentence_audio_file = generate_audio_kannada(kannada)
            st.audio(sentence_audio_file)

            # ---------------------------
            # 🎴 Flashcards per Word
            # ---------------------------
            st.markdown("### 🎴 Flashcards for Each Word")
            words = text.strip().split()
            translated_count = 0

            for word in words:
                try:
                    kannada_word = GoogleTranslator(source="hi", target="kn").translate(word)
                    kannada_in_hindi_word = process("Kannada", "Devanagari", kannada_word)
                    kannada_phonetic = transliterate(kannada_word, sanscript.KANNADA, sanscript.ITRANS)

                    with st.expander(f"Flashcard: {word}"):
                        st.markdown(f"**Hindi:** {word}")
                        st.markdown(f"**Kannada:** {kannada_word}")
                        st.markdown(f"**Kannada in Hindi Letters:** {kannada_in_hindi_word}")
                        st.markdown(f"**Phonetic (English):** `{kannada_phonetic}`")

                        # Word audio
                        word_audio_file = generate_audio_kannada(kannada_word)
                        st.audio(word_audio_file)

                    translated_count += 1
                except Exception:
                    st.warning(f"⚠️ Could not translate: {word}")

            end = time.time()
            st.success(f"✅ Translated {translated_count} word(s) successfully in {end - start:.2f} sec.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Please type some Hindi input!")
