import streamlit as st
import os
import utils
from openai import OpenAI
import base64

def get_audible(raw_text, voice="alloy"):
    client = OpenAI(api_key=st.session_state["cookies"]["OPENAI_API_KEY"])

    completion = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        messages=[
        {
            "role": "system",
            "content": f"You are tasked with creating a podcast titled 'NoteCraft Audible' from this text. Make sure to include all the main ideas and concepts in the text. Make it as engaging as possible and make sure the listenor understands the text. Here is the text: {raw_text}"
        }
    ]
    )

    wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    return wav_bytes

def main():
    utils.universal_setup(
        page_title="Audible",
        page_icon="🎙️",
        upload_file_types=["pdf", "docx", "pptx"],
        worker=False,
    )
    if st.session_state["cookies"].get("model") != "GPT-4o-mini":
        st.error(
            "Audible only works with openAI models."
        )
        st.stop()
    if "audio_output" not in st.session_state:
        st.markdown(
            """
        ### NoteCraft Audible
        NoteCraft Audible is a tool that generates a podcast from a PDF file.
        
        ### How to generate an Audible:
        1. Upload a PDF file.
        2. Select the voice of the speaker.
        3. Select the pages to generate the Audible from.
        4. Click on the "Process" button.
        5. The Audible will be generated and you can listen to it or download it.
        """
        )

    with st.sidebar:
        st.selectbox("Select the voice of the speaker:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        process = st.button("Process", use_container_width=True)
    if st.session_state["file"]:
        file_extension = os.path.splitext(st.session_state["file"].name)[1].lower()
        st.session_state["file_name"] = (
            os.path.splitext(st.session_state["file"].name)[0]
            if st.session_state["file"]
            else "note"
        )
            
        if file_extension in [".pdf", ".docx", ".pptx"]:
            max_pages = utils.page_count(st.session_state["file"])
            if max_pages != 1:
                with st.sidebar:
                    pages = st.slider(
                        "Select the pages to generate notes from: ",
                        value=(1, max_pages),
                        min_value=1,
                        max_value=max_pages,
                    )
            else:
                pages = (1, 1)
                with st.sidebar:
                    st.write("Only one page in the document")
            if process:
                with st.spinner("Processing"):
                    raw_text = utils.get_document_text(
                        st.session_state["file"], page_range=pages
                    )
                    try:
                        st.session_state["audio_output"] =  get_audible(raw_text)
                    except KeyError:
                        st.error(
                            "You don't have access to the selected model. [Get access here](/get_access)."
                        )
                        st.stop()

                    st.session_state["file_name"] = (
                        os.path.splitext(st.session_state["file"].name)[0]
                        if st.session_state["file"]
                        else "note"
                    )
                    st.success("Audible generated!")
        else:
            st.error("The file is not a valid PDF file nor a Markdown file.")
            st.stop()

    if "audio_output" in st.session_state:
        st.audio(st.session_state["audio_output"], format='audio/wav')
        with st.sidebar:
            st.download_button(
                label="Download Audible",
                data=(st.session_state["audio_output"]),
                file_name=f"{st.session_state['file_name']} - NoteCraft Audible.wav",
                mime="text/markdown",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
