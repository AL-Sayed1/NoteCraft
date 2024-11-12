import streamlit as st
import os
import utils


def main():
    utils.universal_setup(
        page_title="Note Generator",
        page_icon="📝",
        upload_file_types=["pdf", "md"],
        worker=True,
    )
    if not st.session_state["file"]:
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
        word_range = st.slider(
            "Select the word range",
            value=(300, 500),
            step=50,
            min_value=100,
            max_value=1500,
        )
        word_range = " to ".join(map(str, word_range))

        process = st.button("Process")
    if st.session_state["file"]:
        file_extension = os.path.splitext(st.session_state["file"].name)[1].lower()
        if file_extension != ".pdf" and file_extension != ".md":
            st.error("The file is not a valid PDF file nor a Markdown file.")
            st.stop()
        elif file_extension == ".md":
            st.session_state["output"] = (
                st.session_state["file"].getvalue().decode("utf-8")
            )
            st.session_state["file_name"] = (
                os.path.splitext(st.session_state["file"].name)[0]
                if st.session_state["file"]
                else "note"
            )
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
                        output = st.session_state["worker"].get_note(
                            raw_text, word_range
                        )
                    except (KeyError, UnboundLocalError):
                        st.error(
                            "You don't have access to the selected model. [Get access here](/get_access)."
                        )
                        st.stop()

                    st.session_state["output"] = utils.md_image_format(
                        output
                        if st.session_state["cookies"]["model"] == "Gemini-1.5"
                        else output.content
                    )
                    st.session_state["file_name"] = (
                        os.path.splitext(st.session_state["file"].name)[0]
                        if st.session_state["file"]
                        else "note"
                    )
                    st.success("Note Crafted!")

    if "output" in st.session_state:
        st.markdown(st.session_state["output"], unsafe_allow_html=True)
        with st.sidebar:
            st.download_button(
                label="Download Note as .md",
                data=st.session_state["output"],
                file_name=f"{st.session_state['file_name']}.md",
                mime="text/markdown",
            )

        usr_suggestion = st.chat_input("Edit the note so that...")
        if usr_suggestion:

            output = st.session_state["worker"].edit(
                task="edit_note",
                text=st.session_state["output"],
                request=usr_suggestion,
            )
            st.session_state["output"] = utils.md_image_format(
                output
                if st.session_state["cookies"]["model"] == "Gemini-1.5"
                else output.content
            )
            st.rerun()


if __name__ == "__main__":
    main()
