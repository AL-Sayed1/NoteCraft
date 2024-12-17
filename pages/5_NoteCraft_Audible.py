import streamlit as st
import os
import utils
from openai import OpenAI
import base64

def get_podcast(raw_text):
    client = OpenAI(api_key=st.session_state["cookies"]["OPENAI_API_KEY"])


    completion = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "wav"},
        messages=[
        {
            "role": "system",
            "content": f"You are tasked with creating a podcast from this text. Make sure to include all the main ideas and concepts in the text. Make it as engaging as possible and make sure the listenor understands the text. Here is the text: {raw_text}"
        }
    ]
    )

    wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    return wav_bytes

def main():
    utils.universal_setup(
        page_title="Note Generator",
        page_icon="🎙️",
        upload_file_types=["pdf"],
        worker=False,
    )
    if "audio_output" not in st.session_state:
        st.markdown(
            """
        ### How to Generate Notes
        1. **Upload your PDF**: Use the file uploader in the sidebar to upload your document.
        2. **Select the word range**: Adjust the slider to set the desired word range for the notes.
        3. **Choose pages (for PDFs)**: Once you uploaded a PDF, select the pages you want to generate notes from.
        4. **Click 'Process'**: Hit the 'Process' button to generate your notes.
        5. **Download or Edit**: Once the notes are generated, you can download them as a Markdown file or edit them using the chat input.
        """
        )

    with st.sidebar:
        process = st.button("Process", use_container_width=True)
    if st.session_state["file"]:
        file_extension = os.path.splitext(st.session_state["file"].name)[1].lower()
        st.session_state["file_name"] = (
            os.path.splitext(st.session_state["file"].name)[0]
            if st.session_state["file"]
            else "note"
        )
        if file_extension != ".pdf":
            st.error("The file is not a valid PDF file nor a Markdown file.")
            st.stop()
        elif file_extension == ".pdf":
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
                    raw_text = utils.get_pdf_text(
                        st.session_state["file"], page_range=pages
                    )
                    try:
                        st.session_state["audio_output"] =  get_podcast(raw_text)
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
                    st.success("podcast generated!")

    if "audio_output" in st.session_state:
        st.audio(st.session_state["audio_output"], format='audio/wav')
        with st.sidebar:
            st.download_button(
                label="Download Podcast",
                data=(st.session_state["audio_output"]),
                file_name=f"{st.session_state['file_name']} - NoteCraft Audible.wav",
                mime="text/markdown",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
