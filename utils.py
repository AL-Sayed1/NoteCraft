import streamlit as st
from os import environ
from streamlit_cookies_manager import EncryptedCookieManager

def universal_setup(page_title="", page_icon="📝", upload_file_types=[]):
    st.set_page_config(page_title=f"NoteCraft AI - {page_title}", page_icon=page_icon, layout="wide")
    hide_button_style = """
    <style>
    .e16jpq800, .ef3psqc6 {
        display: none;
    }
    </style>
"""
    if page_title:
        st.header(f"NoteCraft AI - {page_title}")
    st.markdown(hide_button_style, unsafe_allow_html=True)

    st.session_state["cookies"] = EncryptedCookieManager(
    prefix=environ.get("COOKIES_PREFIX"),
    password=environ.get("COOKIES_PASSWORD"),
)
    if upload_file_types:
        st.session_state["file"] = st.sidebar.file_uploader(
            "upload your file", type=upload_file_types
        )

def display_flashcards(flashcards_data):
    headers = [
        "question",
        "questions",
        "answer",
        "answers",
        "term",
        "terms",
        "definition",
        "definitions",
    ]

    if not flashcards_data:
        st.error("Error Generating Flashcards, No Flashcards generated.")
        return

    if (
        flashcards_data[0][0].strip().lower() in headers
        and flashcards_data[0][1].strip().lower() in headers
    ):
        flashcards_data = flashcards_data[1:]

    st.session_state.questions = [row[0] for row in flashcards_data if len(row) > 1]
    st.session_state.answers = [row[1] for row in flashcards_data if len(row) > 1]

    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    col1, col2, col3 = st.columns(3, gap="small")
    if col1.button("Previous Question"):
        if st.session_state.current_question_index > 0:
            st.session_state.current_question_index -= 1
            st.session_state.show_answer = False
        else:
            st.warning("You are at the first question.")

    if col2.button("Show Answer"):
        st.session_state.show_answer = True

    st.write(f"Total Flashcards {len(st.session_state.questions)}.")

    if col3.button("Next Question"):
        if (
            st.session_state.current_question_index
            < len(st.session_state.questions) - 1
        ):
            st.session_state.current_question_index += 1
            st.session_state.show_answer = False
        else:
            st.warning("You have reached the last question.")

    question = st.session_state.questions[st.session_state.current_question_index]
    st.write(f"Question {st.session_state.current_question_index + 1}: {question}")

    if st.session_state.show_answer:
        answer = st.session_state.answers[st.session_state.current_question_index]
        st.write(f"Answer: {answer}")