import streamlit as st
import os
import base64
import utils


def make_studykit(markdown_content, flashcards, encoded_pdf, page_range):
    unwanted_headers = {
        "Col1": ["question", "questions", "term", "terms"],
        "Col2": ["answer", "answers", "definition", "definitions"],
    }
    rows = flashcards.split("\n")

    headers = rows[0].split("\t")
    if (
        headers[0].lower() in unwanted_headers["Col1"]
        and headers[1].lower() in unwanted_headers["Col2"]
    ):
        rows = rows[1:]
        flashcards = "\n".join(rows)

    if flashcards.startswith("```csv"):
        flashcards = flashcards[5:].lstrip()
    elif flashcards.startswith("``` csv"):
        flashcards = flashcards[6:].lstrip()
    if flashcards.endswith("```"):
        flashcards = flashcards[:-3].rstrip()
    if markdown_content.startswith("```markdown"):
        markdown_content = markdown_content[11:].lstrip()
    elif markdown_content.startswith("``` markdown"):
        markdown_content = markdown_content[12:].lstrip()
    if markdown_content.endswith("```"):
        markdown_content = markdown_content[:-3].rstrip()
    markdown_content = markdown_content.replace("`", r"\`")
    flashcards = flashcards.replace("`", r"\`")

    with open("NoteCraft-StudyKit.html", "r") as file:
        html_template = file.read()

    html_content = html_template.replace("***markdown_content***", markdown_content)
    html_content = html_content.replace("***flashcards***", flashcards.strip())
    html_content = html_content.replace("***encoded_pdf***", encoded_pdf)
    html_content = html_content.replace("***page_range[0]***", str(page_range[0]))
    html_content = html_content.replace("***page_range[1]***", str(page_range[1]))

    return html_content


def main():
    utils.universal_setup(
        page_title="StudyKit",
        page_icon="📚",
        upload_file_types=["pdf"],
        worker=True,
    )
    if "md_output" not in st.session_state:
        st.markdown(
            """
        ### How to Generate Studykit
        1. **Upload your PDF**: Use the file uploader in the sidebar to upload your document.
        2. **Select the word range**: Adjust the slider to set the desired word range for the notes.
        3. **Select the number of flashcards**: Adjust the slider to set the desired flashcard range.
        4. **Select the flashcards type**: Choose either 'Term --> Definition' or 'Question --> Answer' flashcards.
        5. **Choose pages (for PDFs)**: Once you uploaded a PDF, select the pages you want to generate the studykit from.
        6. **Click 'Process'**: Hit the 'Process' button to generate your document.
        7. **Download or Edit**: Once the StudyKit is generated, you can download it or edit it using the chat input.
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
        images = st.checkbox("Include images in the notes", value=True)
        flashcard_type = st.radio(
            "Flashcard Type",
            ["Term --> Definition", "Question --> Answer", "MCQ --> Answer"],
        )

        flashcard_range = st.slider(
            "Select how many flashcards do you want",
            value=(5, 20),
            step=5,
            min_value=5,
            max_value=70,
        )
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
                        st.session_state["file"],
                        page_range=pages,
                    )
                    try:
                        st.session_state["md_AI_output"] = st.session_state[
                            "worker"
                        ].get_note(raw_text, word_range, images)
                        flashcard_output = st.session_state["worker"].get_flashcards(
                            flashcard_range=flashcard_range, task=flashcard_type
                        )

                    except (KeyError, UnboundLocalError):
                        st.error(
                            "You don't have access to the selected model. [Get access here](/get_access)."
                        )
                        st.stop()

                    st.session_state["md_output"] = utils.md_image_format(
                        (
                            st.session_state["md_AI_output"]
                        ),
                        encoded=True,
                    )
                    st.session_state["flashcard_output"] = (
                        flashcard_output
                    )
                    st.session_state["raw_pdf"] = utils.get_base64_encoded_pdf(
                        st.session_state["file"]
                    )
                    st.session_state["output"] = make_studykit(
                        markdown_content=(st.session_state["md_output"]),
                        flashcards=st.session_state["flashcard_output"],
                        encoded_pdf=st.session_state["raw_pdf"],
                        page_range=pages,
                    )
                    st.success("StudyKit Crafted!")
        else:
            st.error("The file is not a valid PDF file.")
            st.stop()

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
            file_name=f"{st.session_state['file_name']} - StudyKit.html",
            mime="application/studykit",
            use_container_width=True,
        )
        st.download_button(
            label="Download Paper Studykit (PDF)",
            data=utils.paper(
                header_text=st.session_state["file_name"],
                markdown_text=st.session_state["md_output"],
                flashcards=st.session_state["flashcard_output"],
            ),
            file_name=f"{st.session_state['file_name']} - studykit.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        col1, col2 = st.columns([3, 1])
        edit_mode = col2.radio("Editing Mode", ["AI Edit", "Manual Edit"])

        if edit_mode == "Manual Edit":
            manual_edit = col1.text_area(
                "Edit your notes directly:",
                value=st.session_state["md_AI_output"],
                height=400,
            )

            if st.button("Apply Changes", use_container_width=True):
                st.session_state["md_output"] = utils.md_image_format(manual_edit)
                st.rerun()

        if edit_mode == "AI Edit":
            usr_suggestion = col1.chat_input("Edit the note so that...")
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

            edit_what = col2.selectbox(label="Edit", options=["Note", "Flashcards"])
            if usr_suggestion:
                if edit_what == "Note":
                    if "md_AI_output" in st.session_state:
                        st.session_state["md_AI_output"] = st.session_state[
                            "worker"
                        ].edit(
                            task="edit_note",
                            text=st.session_state["md_AI_output"],
                            request=usr_suggestion,
                        )
                    
                    st.session_state["md_output"] = utils.md_image_format(
                        (
                            st.session_state["md_AI_output"]
                     ),
                        encoded=True,
                    )
                    st.session_state["output"] = make_studykit(
                        markdown_content=(st.session_state["md_output"]),
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
                    )
                    st.session_state["output"] = make_studykit(
                        markdown_content=(st.session_state["md_output"]),
                        flashcards=st.session_state["flashcard_output"],
                        encoded_pdf=st.session_state["raw_pdf"],
                        page_range=pages,
                    )

                st.rerun()


if __name__ == "__main__":
    main()
