import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, speech_to_text_hindi
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from streamlit_mic_recorder import mic_recorder

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Would you like to answer the questions in Hindi or English?"}
        ]
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "language" not in st.session_state:
        st.session_state.language = None

initialize_session_state()

st.title(":green[Inspire-Bot] 🤖")

footer_container = st.container()

with footer_container:
    cols = st.columns([0.8, 3], gap="small")

with cols[0]:
    audio_bytes = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        just_once=True,
        use_container_width=False,
        callback=None,
        args=(),
        kwargs={},
        key=None
    )
    if audio_bytes:
        audio_bytes = audio_bytes['bytes']

with cols[1]:
    user_text_input = st.text_input("Enter your text query", key="input")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
            f.close()
        
    
        if(st.session_state.language  is not None and st.session_state.language == "hindi"):
            transcript = speech_to_text_hindi(webm_file_path)
        else:
            transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

elif user_text_input:
    st.session_state.messages.append({"role": "user", "content": user_text_input})
    with st.chat_message("user"):
        st.write(user_text_input)

questions_eng = ["What are you doing?", "What is your name?"]
questions_hindi = ["तुम क्या कर रहे हो?", "तुम्हारा नाम क्या है?"]

if st.session_state.messages[-1]["role"] == "user":
    last_user_input = st.session_state.messages[-1]["content"]

    if st.session_state.language is None:
        if last_user_input.lower() in ["english", "hindi"]:
            st.session_state.language = last_user_input.lower()

    if st.session_state.language:
        questions = questions_eng if st.session_state.language == "english" else questions_hindi
        question_index = st.session_state.question_index

        if question_index < len(questions):
            question = questions[question_index]
            st.session_state.messages.append({"role": "assistant", "content": question})
            with st.chat_message("assistant"):
                audio = text_to_speech(question)
                autoplay_audio(audio)
                st.write(question)
                os.remove(audio)
            st.session_state.question_index += 1
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Thank you for answering all the questions!"})
            with st.chat_message("assistant"):
                st.write("Thank you for answering all the questions!")

