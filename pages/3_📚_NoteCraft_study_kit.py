import streamlit as st
from llm_worker import worker, md_image_format
from pdf_handler import page_count, get_pdf_text
import os
import base64
import csv
import io
import utils

def get_base64_encoded_pdf(file):
    file.seek(0)
    pdf_content = file.read()
    encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")
    return encoded_pdf


def make_webpage(markdown_content, flashcards, encoded_pdf, page_range):
    unwanted_headers = {
        "Col1": ["question", "questions", "term", "terms"],
        "Col2": ["answer", "answers", "definition", "definitions"],
    }
    rows = flashcards.split("\n")

    headers = rows[0].split("\t")
    if (
        headers[0].strip().lower() in unwanted_headers["Col1"]
        and headers[1].strip().lower() in unwanted_headers["Col2"]
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

    with open("studykit-template.min.html", "r") as file:
        html_template = file.read()

    html_content = html_template.replace("***markdown_content***", markdown_content)
    html_content = html_content.replace("***flashcards***", flashcards.strip())
    html_content = html_content.replace("***encoded_pdf***", encoded_pdf)
    html_content = html_content.replace("***page_range[0]***", str(page_range[0]))
    html_content = html_content.replace("***page_range[1]***", str(page_range[1]))

    return html_content


def main():
    utils.universal_setup(page_title="StudyKit", page_icon="📚", upload_file_types=["pdf"])
    if (
        "md_output" not in st.session_state
        and "flashcard_output" not in st.session_state
        and "output" not in st.session_state
    ):
        st.markdown("""
        ### How to Generate Studykit
        1. **Upload your PDF**: Use the file uploader in the sidebar to upload your document.
        2. **Select the word range**: Adjust the slider to set the desired word range for the notes.
        3. **Select the number of flashcards**: Adjust the slider to set the desired flashcard range.
        4. **Select the flashcards type**: Choose between 'Term --> Definition' or 'Question --> Answer' flashcards.
        5. **Choose pages (for PDFs)**: Once you uploaded a PDF, select the pages you want to generate the studykit from.
        6. **Click 'Process'**: Hit the 'Process' button to generate your flashcards.
        7. **Download or Edit**: Once the flashcards are generated, you can download them as a csv file or edit them using the chat input.
        """)
    with st.sidebar:
        word_range = st.slider(
            "Select the word range of the note:",
            value=(200, 300),
            step=50,
            min_value=50,
            max_value=1000,
        )
        word_range = " to ".join(map(str, word_range))
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
        if file_extension != ".pdf":
            st.error("The file is not a valid PDF file.")
            st.stop()
        else:
            max_pages = page_count(st.session_state["file"])
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
                    try:
                        note_chain = worker(
                            cookies=st.session_state["cookies"]
                        ).get_chain()
                        flashcard_chain = worker(
                            task=flashcard_type, cookies=st.session_state["cookies"]
                        ).get_chain()
                    except (KeyError, UnboundLocalError):
                        st.error("You don't have access to the selected model. [Get access here](/get_access).")
                        st.stop()
                    raw_text = get_pdf_text(st.session_state["file"], page_range=pages)

                    st.session_state["md_AI_output"] = note_chain.invoke(
                        {"transcript": raw_text, "word_range": word_range}
                    )
                    flashcard_output = flashcard_chain.invoke(
                        {
                            "transcript": raw_text,
                            "flashcard_range": flashcard_range,
                        }
                    )
                    st.session_state["md_output"] = md_image_format(
                        st.session_state["md_AI_output"]
                        if st.session_state["cookies"]["model"] == "Gemini-1.5"
                        else st.session_state["md_AI_output"].content,
                        encoded=True,
                    )
                    st.session_state["flashcard_output"] = (
                        flashcard_output
                        if st.session_state["cookies"]["model"] == "Gemini-1.5"
                        else flashcard_output.content
                    )
                    st.session_state["file_name"] = (
                        os.path.splitext(st.session_state["file"].name)[0]
                        if st.session_state["file"]
                        else "note"
                    )
                    st.session_state["raw_pdf"] = get_base64_encoded_pdf(
                        st.session_state["file"]
                    )
                    st.session_state["output"] = make_webpage(
                        markdown_content=st.session_state["md_output"],
                        flashcards=st.session_state["flashcard_output"],
                        encoded_pdf=st.session_state["raw_pdf"],
                        page_range=pages,
                    )
                    st.success("StudyKit Crafted!")

    if (
        "md_output" in st.session_state
        and "flashcard_output" in st.session_state
        and "output" in st.session_state
    ):
        st.markdown("# Notes:")
        st.markdown(st.session_state["md_output"], unsafe_allow_html=True)
        flashcards_io = io.StringIO(st.session_state["flashcard_output"])
        try:
            flashcards_reader = csv.reader(flashcards_io, delimiter="\t")
            flashcards_data = list(flashcards_reader)
        except csv.Error:
            st.error("There was an error generating the flashcards, please try again.")
            st.write(st.session_state["flashcard_output"])
            st.stop()
        utils.display_flashcards(flashcards_data)
        st.download_button(
            label="Download Study kit",
            data=st.session_state["output"],
            file_name=f"{st.session_state['file_name']}.html",
            mime="text/html",
            use_container_width=True,
        )

        col1, col2 = st.columns([3, 1])
        usr_suggestion = col1.chat_input("Edit the note so that...")
        edit_what = col2.selectbox(label="Edit", options=["Note", "Flashcards"])
        if usr_suggestion:
            if edit_what == "Note":
                editor = worker(task="edit_note", cookies=st.session_state["cookies"])
                editor_chain = editor.get_chain()
                st.session_state["md_AI_output"] = editor_chain.invoke(
                    {
                        "request": usr_suggestion,
                        "note": st.session_state["md_AI_output"],
                    }
                )
                st.session_state["md_output"] = md_image_format(
                    st.session_state["md_AI_output"]
                    if st.session_state["cookies"]["model"] == "Gemini-1.5"
                    else st.session_state["md_AI_output"].content,
                    encoded=True,
                )
                st.session_state["output"] = make_webpage(
                    markdown_content=st.session_state["md_output"],
                    flashcards=st.session_state["flashcard_output"],
                    encoded_pdf=st.session_state["raw_pdf"],
                    page_range=pages,
                )

            elif edit_what == "Flashcards":
                editor = worker(
                    task="edit_flashcard", cookies=st.session_state["cookies"]
                )
                editor_chain = editor.get_chain()
                output = editor_chain.invoke(
                    {
                        "request": usr_suggestion,
                        "flashcards": st.session_state["flashcard_output"],
                    }
                )
                st.session_state["flashcard_output"] = (
                    output
                    if st.session_state["cookies"]["model"] == "Gemini-1.5"
                    else output.content
                )
                st.session_state["output"] = make_webpage(
                    markdown_content=st.session_state["md_output"],
                    flashcards=st.session_state["flashcard_output"],
                    encoded_pdf=st.session_state["raw_pdf"],
                    page_range=pages,
                )

            st.rerun()


if __name__ == "__main__":
    main()
