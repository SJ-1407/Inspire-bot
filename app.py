import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, speech_to_text_hindi
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from streamlit_mic_recorder import mic_recorder
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

float_init()

prompt = ChatPromptTemplate.from_messages([
    ("system",
    '''You are a chatbot for that is being used for gathering information from the user. You can ask me questions and I will try to answer them to the best of my ability.
You do not have to ask random questions.You will be provided with a question that was asked to the user and the corresponding answer of the user. Now based on tyhe question and user's answer, if you are unsatisfied with the user's answer , and believe there is some missing information, upu may ask the questions to the user that would help in completing the quesiton. If you do not wish to ask any questions,just reply with No questions.
Make sure to ask the question in a format like a human would ask it in the conversation, so that user is able to answer them easily.
Make sure to ask the questions in the same langaugae as taht of the user.
Here is the question asked to the user:
{question}
Below is the answer provided by the user:
{answer}'''),]
)

model=ChatOpenAI(model="gpt-4o")
chain=prompt|model
sub_questions=" "

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
            sub_questions=chain.invoke({"question":st.session_state.messages[-1]["content"],"answer":transcript}).content
            
        else:
            transcript = speech_to_text(webm_file_path)
            sub_questions=chain.invoke({"question":st.session_state.messages[-1]["content"],"answer":transcript}).content
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

elif user_text_input:
    sub_questions=chain.invoke({"question":st.session_state.messages[-1]["content"],"answer":user_text_input}).content

    st.session_state.messages.append({"role": "user", "content": user_text_input})
    with st.chat_message("user"):
        st.write(user_text_input)

questions_eng = ["What are you doing?", "What is your name?"]
questions_hindi = ["तुम क्या कर रहे हो?", "तुम्हारा नाम क्या है?"]

if sub_questions!="No questions." and sub_questions!=" ":
    print(type(sub_questions),sub_questions)
    st.session_state.messages.append({"role": "assistant", "content": sub_questions})
    with st.chat_message("assistant"):
        audio = text_to_speech(sub_questions)
        autoplay_audio(audio)
        st.write(sub_questions)
        os.remove(audio)

else:
    print(sub_questions)

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

