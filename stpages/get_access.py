import os
import streamlit as st
import requests
import openai

def validate_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True

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

    model_options = {
        "Gemini-1.5": "GOOGLE_API_KEY",
        "GPT-4o": "OPENAI_API_KEY"
    }

    selected_model = st.selectbox(
        "Select the model you want to access:",
        list(model_options.keys()),
        index=list(model_options.keys()).index(st.session_state["cookies"]["model"]) if "model" in st.session_state["cookies"] else 0
    )

    api_title = model_options[selected_model]
    
    value = st.session_state["cookies"].get(api_title, "")

    API_KEY = st.text_input(
        "GOOGLE API KEY:" if api_title == "GOOGLE_API_KEY" else "OPENAI API KEY:",
        type="password",
        value=value
    )

    if st.button("SAVE") and API_KEY:
        st.session_state["cookies"][api_title] = API_KEY
        st.session_state["cookies"]["model"] = selected_model
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
        f"Get the api key from the [Google AI studio](https://aistudio.google.com/)."
    )

if __name__ == "__main__":
    main()