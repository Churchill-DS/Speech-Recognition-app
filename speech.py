import streamlit as st
import speech_recognition as sr
import time
import threading

# Initialize session state variables
if "transcription" not in st.session_state:
    st.session_state.transcription = ""
if "listening" not in st.session_state:
    st.session_state.listening = False
if "stop_signal" not in st.session_state:
    st.session_state.stop_signal = False

def list_apis():
    return {
        "google": "Google Web Speech API",
        "sphinx": "CMU Sphinx (offline)"
    }

def transcribe_speech(api_choice="google", language="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return "[Error] Listening timed out. Try speaking sooner."

    try:
        if api_choice == "google":
            return recognizer.recognize_google(audio, language=language)
        elif api_choice == "sphinx":
            return recognizer.recognize_sphinx(audio, language=language)
        else:
            return "[Error] Unsupported API selected."
    except sr.UnknownValueError:
        return "[Error] Could not understand audio."
    except sr.RequestError as e:
        return f"[Error] API request failed: {e}"

def save_transcript(text, filename="transcript.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def listen_loop(api, lang):
    while not st.session_state.stop_signal:
        result = transcribe_speech(api_choice=api, language=lang)
        if not result.startswith("[Error]"):
            st.session_state.transcription += result + "\n"
            save_transcript(result)
        else:
            st.warning(result)
        time.sleep(1)  # Prevents tight infinite loop

# --- Streamlit Interface ---

st.title("🎙️ Live Speech Recognition App")

st.sidebar.header("Settings")

api_choice = st.sidebar.selectbox("Choose API", options=list(list_apis().keys()), format_func=lambda x: list_apis()[x])
language = st.sidebar.text_input("Language Code", value="en-US")

st.sidebar.markdown("---")
start_button = st.sidebar.button("▶️ Start Listening")
pause_button = st.sidebar.button("⏸️ Pause Listening")
reset_button = st.sidebar.button("🔄 Reset Transcript")

st.markdown("### 📝 Live Transcription")
st.text_area("Transcript:", value=st.session_state.transcription, height=300)

if start_button:
    st.session_state.stop_signal = False
    st.session_state.listening = True
    threading.Thread(target=listen_loop, args=(api_choice, language), daemon=True).start()

if pause_button:
    st.session_state.stop_signal = True
    st.session_state.listening = False
    st.success("Paused Listening.")

if reset_button:
    st.session_state.transcription = ""
    st.success("Transcript reset.")

st.sidebar.markdown("---")
st.sidebar.write("Created with using Streamlit and SpeechRecognition.")
