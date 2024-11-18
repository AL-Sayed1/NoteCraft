import streamlit as st
import os
import base64
import utils


def make_studykit(markdown_content, flashcards, encoded_pdf, page_range):
    flashcards = utils.clean_flashcards(flashcards)

    markdown_content = markdown_content.replace("`", r"\`")

    studkit = f"""note=`^{markdown_content}`^
flashcards=`^{flashcards.strip()}`^
encoded_pdf=`^{encoded_pdf}`^

page_range=`^{str(page_range[0])} to {str(page_range[1])}`^"""

    return studkit


def main():
    utils.universal_setup(
        page_title="StudyKit",
        page_icon="📚",
        upload_file_types=["pdf", "studkit"],
        worker=True,
    )
    if not st.session_state["file"]:
        st.markdown(
            """
        ### How to Generate Studykit
        1. **Upload your PDF**: Use the file uploader in the sidebar to upload your document.
        2. **Select the word range**: Adjust the slider to set the desired word range for the notes.
        3. **Select the number of flashcards**: Adjust the slider to set the desired flashcard range.
        4. **Select the flashcards type**: Choose between 'Term --> Definition' or 'Question --> Answer' flashcards.
        5. **Choose pages (for PDFs)**: Once you uploaded a PDF, select the pages you want to generate the studykit from.
        6. **Click 'Process'**: Hit the 'Process' button to generate your flashcards.
        7. **Download or Edit**: Once the StudyKit is generated, you can download it or edit it using the chat input.
        8. **Download StudyKit Viewer**: Download the StudyKit viewer to view the StudyKit!
        """
        )
    with open("NoteCraft-StudyKit.html", "r") as file:
        st.download_button(
            label="Download StudyKit viewer",
            data=file.read(),
            file_name="NoteCraft-StudyKit.html",
            mime="text/html",
            use_container_width=True,
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
        images = st.checkbox("Include images in the notes", value=True)
        flashcard_type = st.radio(
            "Flashcard Type", ["Term --> Definition", "Question --> Answer"]
        )

        flashcard_range = st.slider(
            "Select how many flashcards do you want",
            value=(5, 20),
            step=5,
            min_value=5,
            max_value=70,
        )

        process = st.button("Process")
    if st.session_state["file"]:
        file_extension = os.path.splitext(st.session_state["file"].name)[1].lower()
        st.session_state["file_name"] = (
            os.path.splitext(st.session_state["file"].name)[0]
            if st.session_state["file"]
            else "note"
        )
        if file_extension != ".pdf" and file_extension != ".studkit":
            st.error("The file is not a valid PDF file.")
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
                        st.session_state["file"],
                        page_range=pages,
                    )
                    try:
                        st.session_state["md_AI_output"] = st.session_state[
                            "worker"
                        ].get_note(raw_text, word_range, images)
                        flashcard_output = st.session_state["worker"].get_flashcards(
                            flashcard_range=flashcard_range,
                            task=flashcard_type
                        )

                    except (KeyError, UnboundLocalError):
                        st.error(
                            "You don't have access to the selected model. [Get access here](/get_access)."
                        )
                        st.stop()

                    st.session_state["md_output"] = utils.md_image_format(
                        (
                            st.session_state["md_AI_output"]
                            if st.session_state["cookies"]["model"] == "Gemini-1.5"
                            else st.session_state["md_AI_output"].content
                        ),
                        encoded=True,
                    )
                    st.session_state["flashcard_output"] = (
                        flashcard_output
                        if st.session_state["cookies"]["model"] == "Gemini-1.5"
                        else flashcard_output.content
                    )
                    st.session_state["raw_pdf"] = utils.get_base64_encoded_pdf(
                        st.session_state["file"]
                    )
                    st.session_state["output"] = make_studykit(
                        markdown_content=st.session_state["md_output"],
                        flashcards=st.session_state["flashcard_output"],
                        encoded_pdf=st.session_state["raw_pdf"],
                        page_range=pages,
                    )
                    st.success("StudyKit Crafted!")
        elif file_extension == ".studkit":
            file_content = st.session_state["file"].getvalue().decode("utf-8")
            st.session_state["md_output"], st.session_state["flashcard_output"] = (
                flashcards
            ) = utils.parse_studkit(file_content)
            st.session_state["output"] = file_content
            st.success("StudyKit Loaded!")

    if (
        "md_output" in st.session_state
        and "flashcard_output" in st.session_state
        and "output" in st.session_state
    ):
        st.markdown("# Notes:")
        st.markdown(st.session_state["md_output"], unsafe_allow_html=True)
        st.markdown("# Flashcards:")
        utils.display_flashcards(st.session_state["flashcard_output"])
        st.download_button(
            label="Download Study kit",
            data=st.session_state["output"],
            file_name=f"{st.session_state['file_name']}.studkit",
            mime="application/studykit",
            use_container_width=True,
        )
        st.download_button(
            label="Download Paper Studykit (PDF)",
            data=utils.paper_studykit(markdown_text=st.session_state["md_output"], header_text=st.session_state['file_name'], flashcards=st.session_state["flashcard_output"]),
            file_name=f"{st.session_state['file_name']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        col1, col2 = st.columns([3, 1])
        usr_suggestion = col1.chat_input("Edit the note so that...")
        edit_what = col2.selectbox(label="Edit", options=["Note", "Flashcards"])
        if usr_suggestion:
            if edit_what == "Note":
                try:
                    st.session_state["md_AI_output"] = st.session_state["worker"].edit(
                        task="edit_note",
                        text=st.session_state["md_AI_output"],
                        request=usr_suggestion,
                    )
                except KeyError:
                    st.error(
                        "Cannot edit a note loaded from a studkit file, you can only edit flashcards from a studkit file."
                    )
                    st.stop()
                st.session_state["md_output"] = utils.md_image_format(
                    (
                        st.session_state["md_AI_output"]
                        if st.session_state["cookies"]["model"] == "Gemini-1.5"
                        else st.session_state["md_AI_output"].content
                    ),
                    encoded=True,
                )
                st.session_state["output"] = make_studykit(
                    markdown_content=st.session_state["md_output"],
                    flashcards=st.session_state["flashcard_output"],
                    encoded_pdf=st.session_state["raw_pdf"],
                    page_range=pages,
                )

            elif edit_what == "Flashcards":

                output = st.session_state["worker"].edit(
                    task="edit_flashcards",
                    text=st.session_state["flashcard_output"],
                    request=usr_suggestion,
                )
                st.session_state["flashcard_output"] = (
                    output
                    if st.session_state["cookies"]["model"] == "Gemini-1.5"
                    else output.content
                )
                st.session_state["output"] = make_studykit(
                    markdown_content=st.session_state["md_output"],
                    flashcards=st.session_state["flashcard_output"],
                    encoded_pdf=st.session_state["raw_pdf"],
                    page_range=pages,
                )

            st.rerun()


if __name__ == "__main__":
    main()
