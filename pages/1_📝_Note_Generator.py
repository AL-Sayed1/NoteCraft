import streamlit as st
import os
import utils


def main():
    utils.universal_setup(
        page_title="Note Generator",
        page_icon="📝",
        upload_file_types=["pdf", "md","docx", "pptx"],
        yt_upload = True,
        worker=True,
    )
    if "md_output" not in st.session_state:
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
        st.write(st.session_state["cookies"]["model"])
        word_range = st.slider(
            "Select the word range",
            value=(300, 500),
            step=50,
            min_value=100,
            max_value=1500,
        )
        images = st.checkbox("Include images in the notes", value=True)
        process = st.button("Process", use_container_width=True)

    if st.session_state["upload"][0] == "file" and st.session_state["upload"][1] is not None:
        st.session_state["file_name"], file_extension = os.path.splitext(st.session_state["upload"][1].name)
        file_extension = file_extension.lower()
        if file_extension == ".md":
            st.session_state["md_output"] = (
                st.session_state["upload"][1].getvalue().decode("utf-8")
            )

        elif file_extension in [".pdf", ".docx", ".pptx"]:
            max_pages = utils.page_count(st.session_state["upload"][1])
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
        else:
            st.error("The file is not a valid PDF file nor a Markdown file.")
            st.stop()
        
    if process:
        with st.spinner("Processing"):
            if st.session_state["upload"][0] == "file" and st.session_state["upload"][1] is not None:
                raw_text = utils.get_document_text(
                    st.session_state["upload"][1], page_range=pages
                )
            elif st.session_state["upload"][0] == "youtube" and st.session_state["upload"][1] is not None:
                raw_text = utils.fetch_transcript(st.session_state["upload"][1])
                st.session_state["file_name"] = "NoteCraft Video Notes"
            else:
                st.write(st.session_state["upload"])
                st.error("No file uploaded")
                st.stop()
            try:
                st.session_state["md_AI_output"] = st.session_state["worker"].get_note(raw_text, word_range, images)
            except KeyError:
                st.error(
                    "You don't have access to the selected model. [Get access here](/get_access)."
                )
                st.stop()

            st.session_state["md_output"] = utils.md_image_format(
                st.session_state["md_AI_output"]
            )

            st.success("Note Crafted!")

    if "md_output" in st.session_state:
        st.markdown("# Notes:")
        st.markdown(st.session_state["md_output"], unsafe_allow_html=True)
        with st.sidebar:
            st.download_button(
                label="Download Note as .md",
                data=(st.session_state["md_output"]),
                file_name=f"{st.session_state['file_name']}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.download_button(
                label="Download Paper Notes (PDF)",
                data=utils.paper(
                    header_text=st.session_state["file_name"],
                    markdown_text=st.session_state["md_output"],
                ),
                file_name=f"{st.session_state['file_name']} - Notes.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        edit_mode = st.radio("Editing Mode", ["AI Edit", "Manual Edit"])

        if edit_mode == "Manual Edit":
            manual_edit = st.text_area(
                "Edit your notes directly:",
                value=st.session_state["md_output"],
                height=400,
            )

            if st.button("Apply Changes", use_container_width=True):
                st.session_state["md_output"] = utils.md_image_format(manual_edit)
                st.rerun()

        if edit_mode == "AI Edit":
            usr_suggestion = st.chat_input("Edit the note so that...")
            if usr_suggestion:
                st.session_state["md_AI_output"] = st.session_state["worker"].edit(
                    task="edit_note",
                    text=st.session_state["md_output"],
                    request=usr_suggestion,
                )
                st.session_state["md_output"] = utils.md_image_format(
                    st.session_state["md_AI_output"]
                )
                st.rerun()


if __name__ == "__main__":
    main()
