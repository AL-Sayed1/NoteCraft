import os
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import requests


def validate_Google_api_key(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    request = requests.get(url)
    print(request)
    if request.status_code == 200:
        return True
    else:
        return False


def main():

    if not st.session_state["cookies"].ready():
        # Wait for the component to load and send us current cookies.
        st.stop()


    if "GOOGLE_API_KEY" in st.session_state["cookies"]:
        st.success(
            "You have already set the API key, you can change it if it doesn't work."
        )


    GOOGLE_API_KEY = st.text_input(
        "GOOGLE API KEY:",
        type="password",
        value=st.session_state["cookies"]["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.session_state["cookies"] else "",
    )
    


    if st.button("SAVE") and GOOGLE_API_KEY:
        st.session_state["cookies"]["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        st.session_state["cookies"].save()
        if (
            st.session_state["cookies"]["GOOGLE_API_KEY"] == GOOGLE_API_KEY
        ):
            if validate_Google_api_key(GOOGLE_API_KEY):
                st.success(
                    "Access has been granted successfully! You can now use NoteCraft AI!"
                )
            elif validate_Google_api_key(GOOGLE_API_KEY) == False:
                st.error("Google API key seems invalid.")
            else:
                st.error("API key seem invalid.")
        else:
            st.error("There was an error while saving the API keys :(")

    st.caption(
        f"Get the api key from the [Google AI studio](https://aistudio.google.com/)."
    )


if __name__ == "__main__":
    main()