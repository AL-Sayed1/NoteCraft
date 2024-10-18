import streamlit as st

st.set_page_config(page_title="NoteCraft AI", page_icon="📝", layout="wide")

from stpages import (
    Flashcard_Generator,
    Note_generator,
    NoteCraft_study_kit,
    get_access,
    about,
)
from streamlit_option_menu import option_menu


from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager
from os import environ

load_dotenv()

st.session_state["cookies"] = EncryptedCookieManager(
    prefix=environ.get("COOKIES_PREFIX"),
    password=environ.get("COOKIES_PASSWORD"),
)

hide_button_style = """
    <style>
    .e16jpq800, .ef3psqc6 {
        display: none;
    }
    </style>
"""
st.markdown(hide_button_style, unsafe_allow_html=True)

st.session_state["file"] = st.sidebar.file_uploader(
    "upload your PDF or CSV", type=["pdf", "csv", "md"]
)

selected_page = option_menu(
    menu_title=None,
    options=["Note Craft", "Flashcard Craft", "StudyKit", "Get Access", "About"],
    icons=[
        "pen-fill",
        "card-text",
        "suitcase-lg",
        "unlock-fill",
        "question-lg",
    ],
    orientation="horizontal",
)

if selected_page == "Note Craft":
    Note_generator.main()
elif selected_page == "Flashcard Craft":
    Flashcard_Generator.main()
elif selected_page == "StudyKit":
    NoteCraft_study_kit.main()
elif selected_page == "Get Access":
    get_access.main()
elif selected_page == "About":
    about.main()
