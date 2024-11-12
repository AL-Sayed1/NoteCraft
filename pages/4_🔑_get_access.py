import os
import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager
from os import environ
import utils


def validate_openai_api_key(api_key):
    url = "https://api.openai.com/v1/models/gpt-4o"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False


def validate_Google_api_key(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    request = requests.get(url)
    print(request)
    if request.status_code == 200:
        return True
    else:
        return False


def main():
    utils.universal_setup(page_title="Get Access", page_icon="🔑")
    if not st.session_state["cookies"].ready():
        # Wait for the component to load and send us current cookies.
        st.stop()

    model_options = {"Gemini-1.5": "GOOGLE_API_KEY", "GPT-4o-mini": "OPENAI_API_KEY"}

    model_list = list(model_options.keys())
    selected_model_key = st.session_state["cookies"].get("model", None)

    if selected_model_key in model_list:
        selected_index = model_list.index(selected_model_key)
    else:
        selected_index = 0

    selected_model = st.selectbox(
        "Select the model you want to access:", model_list, index=selected_index
    )

    api_title = model_options[selected_model]

    value = st.session_state["cookies"].get(api_title, "")

    API_KEY = st.text_input(
        "GOOGLE API KEY:" if api_title == "GOOGLE_API_KEY" else "OPENAI API KEY:",
        type="password",
        value=value,
    )
    PageWise = st.toggle(
        "PageWise Summaries (experemental)",
        value=st.session_state["cookies"].get("pageWise", "False") == "True",
        help="May use more API calls, but can craft notes and flashcards from large ducuments without missing a detail. **Not recommended for free API keys**.",
    )

    if st.button("SAVE") and API_KEY:

        st.session_state["cookies"][api_title] = API_KEY
        st.session_state["cookies"]["model"] = selected_model
        st.session_state["cookies"]["pageWise"] = str(PageWise)
        st.session_state["cookies"].save()
        if st.session_state["cookies"][api_title] == API_KEY:
            if api_title == "GOOGLE_API_KEY":
                if validate_Google_api_key(API_KEY):
                    st.success(
                        "Access has been granted successfully! You can now use NoteCraft AI!"
                    )
                elif validate_Google_api_key(API_KEY) == False:
                    st.error("Google API key seems invalid.")
                else:
                    st.error("API key seem invalid.")
            elif api_title == "OPENAI_API_KEY":
                if validate_openai_api_key(API_KEY):
                    st.success(
                        "Access has been granted successfully! You can now use NoteCraft AI!"
                    )
                elif validate_openai_api_key(API_KEY) == False:
                    st.error("OpenAI API key seems invalid.")
                else:
                    st.error("API key seem invalid.")
        else:
            st.error("There was an error while saving the API keys :(")

    st.caption(
        f"Get the API key from the [Google AI studio](https://aistudio.google.com/app/apikey)."
    )


if __name__ == "__main__":
    main()
