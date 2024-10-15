import streamlit as st
from llm_worker import worker, md_image_format
from pdf_handler import page_count, get_pdf_text
import streamlit as st
import os
import pdf_handler
from llm_worker import worker
import base64
import pandas as pd
import io
from stpages.Flashcard_Generator import display_flashcards


def get_base64_encoded_pdf(file):
    file.seek(0)
    pdf_content = file.read()
    encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")
    return encoded_pdf


def make_webpage(markdown_content, flashcards, encoded_pdf, page_range):
    html_template = f"""
<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>NoteCraft StudyKit</title> <style> body {{ font-family: serif; margin: 20px; background-color: #cfd6e3; color: #333; }} h1 {{ text-align: center; color: #ff4b4b; }} .toc, .markdown, .pdf-container, .flashcards, .downloads {{ background: #fff; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }} .toc h2, .markdown h2, .pdf-container h2, .flashcards h2, .downloads h2 {{ color: #ff4b4b; }} .toc ul {{ list-style-type: none; padding: 0; }} .toc li {{ margin: 10px 0; }} .toc a {{ text-decoration: none; color: #ff4b4b; font-weight: bold; }} .toc a:hover {{ text-decoration: underline; }} iframe {{ width: 100%; height: 600px; border: none; border-radius: 8px; }} .markdown img {{ display: block; margin: 0 auto; max-width: 100%; max-height: 500px; }} .flashcard {{ text-align: center; margin: 20px 0; }} .flashcard .term {{ font-size: 1.5em; font-weight: bold; }} .flashcard .definition {{ display: none; margin-top: 10px; font-size: 1.2em; }} .flashcard button {{ margin: 10px; padding: 10px 20px; font-size: 1em; border: none; border-radius: 5px; background-color: #ff4b4b; color: #fff; cursor: pointer; }} .flashcard button:hover {{ background-color: #e04343; }} .flashcard .question-number {{ margin-top: 10px; font-size: 0.8em; }} .downloads button {{ margin: 10px; padding: 10px 20px; font-size: 1em; border: none; border-radius: 5px; background-color: #ff4b4b; color: #fff; cursor: pointer; }} .downloads button:hover {{ background-color: #e04343; }} </style> <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script></head><body> <h1>NoteCraft StudyKit</h1> <div class="toc"> <h2>Table of Contents</h2> <ul id="toc-list"></ul> </div> <div class="markdown" id="markdown-content"> <!-- Markdown content will be injected here --> </div> <div class="flashcards"> <h2>Flashcards</h2> <div class="flashcard"> <button id="prev-question">Previous</button> <button id="show-answer">Show Answer</button> <button id="next-question">Next</button> <div class="question-number" id="question-number"></div> <div class="term" id="flashcard-term"></div> <div class="definition" id="flashcard-definition"></div> </div> </div> <div class="pdf-container"> <h2>Reference PDF</h2> <p>StudyKit is generated from pages {page_range[0]} to {page_range[1]}</p> <iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="600px"></iframe> </div> <div class="downloads"> <h2>Downloads</h2> <button id="download-pdf">Download PDF</button> <button id="download-flashcards">Download Flashcards</button> <button id="download-notes">Download Notes</button> </div> <script> document.addEventListener("DOMContentLoaded", function() {{ const markdownContent = `{markdown_content}`; const markdownContainer = document.getElementById('markdown-content'); markdownContainer.innerHTML = marked.parse(markdownContent); const tocList = document.getElementById('toc-list'); const headers = markdownContainer.querySelectorAll('h1, h2, h3, h4, h5, h6'); headers.forEach((header, index) => {{ const id = `header-${{index}}`; header.id = id; const listItem = document.createElement('li'); const link = document.createElement('a'); link.href = `#${{id}}`; link.textContent = header.textContent; listItem.appendChild(link); tocList.appendChild(listItem); }}); const csvData = `{flashcards}`; const flashcards = csvData.split('\\n').map(row => {{ const [term, definition] = row.split('\\t'); return {{ term, definition }}; }}); let currentIndex = 0; const termElement = document.getElementById('flashcard-term'); const definitionElement = document.getElementById('flashcard-definition'); const questionNumberElement = document.getElementById('question-number'); const showAnswerButton = document.getElementById('show-answer'); const prevQuestionButton = document.getElementById('prev-question'); const nextQuestionButton = document.getElementById('next-question'); function updateFlashcard() {{ const flashcard = flashcards[currentIndex]; termElement.textContent = flashcard.term; definitionElement.textContent = flashcard.definition; definitionElement.style.display = 'none'; showAnswerButton.textContent = 'Show Answer'; questionNumberElement.textContent = `Question ${{currentIndex + 1}} out of ${{flashcards.length}}`; }} showAnswerButton.addEventListener('click', () => {{ if (definitionElement.style.display === 'none') {{ definitionElement.style.display = 'block'; showAnswerButton.textContent = 'Hide Answer'; }} else {{ definitionElement.style.display = 'none'; showAnswerButton.textContent = 'Show Answer'; }} }}); prevQuestionButton.addEventListener('click', () => {{ currentIndex = (currentIndex - 1 + flashcards.length) % flashcards.length; updateFlashcard(); }}); nextQuestionButton.addEventListener('click', () => {{ currentIndex = (currentIndex + 1) % flashcards.length; updateFlashcard(); }}); updateFlashcard(); function downloadFile(filename, content, mimeType) {{ const element = document.createElement('a'); element.setAttribute('href', `data:${{mimeType}};charset=utf-8,` + encodeURIComponent(content)); element.setAttribute('download', filename); element.style.display = 'none'; document.body.appendChild(element); element.click(); document.body.removeChild(element); }} document.getElementById('download-pdf').addEventListener('click', () => {{ downloadFile('StudyKit.pdf', `{encoded_pdf}`, 'application/pdf'); }}); document.getElementById('download-flashcards').addEventListener('click', () => {{ downloadFile('flashcards.csv', csvData, 'text/csv'); }}); document.getElementById('download-notes').addEventListener('click', () => {{ downloadFile('notes.md', markdownContent, 'text/markdown'); }}); }}); </script></body></html>
"""
    return html_template


def main():
    st.header("NoteCraft AI - StudyKit")

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
            max_value=200,
        )

        process = st.button("Process")
    if st.session_state["file"]:
        file_extension = os.path.splitext(st.session_state["file"].name)[1].lower()
        if file_extension != ".pdf":
            st.error("The file is not a valid PDF file.")
            st.stop()
        else:
            max_pages = pdf_handler.page_count(st.session_state["file"])
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
                        note_chain = worker(cookies=st.session_state["cookies"]).get_chain()
                        flashcard_chain = worker(task=flashcard_type, cookies=st.session_state["cookies"]).get_chain()
                    except KeyError:
                        st.error(f"The API key is not set.")
                        st.stop()
                    raw_text = pdf_handler.get_pdf_text(
                        st.session_state["file"], page_range=pages
                    )
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
                        st.session_state["md_AI_output"].content, encoded=True
                    )
                    st.session_state["flashcard_output"] = flashcard_output.content
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
            flashcards_df = pd.read_csv(flashcards_io, sep="\t", header=None)
        except pd.errors.ParserError:
            st.error("There was an error generating the flashcards, please try again.")
            st.stop()
        display_flashcards(flashcards_df)
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
                editor = worker("edit_note", cookies=st.session_state["cookies"])
                editor_chain = editor.get_chain()
                md_output = editor_chain.invoke(
                    {
                        "request": usr_suggestion,
                        "note": st.session_state["md_AI_output"],
                    }
                )
                st.session_state["md_output"] = md_image_format(
                    md_output.content, encoded=True
                )
                st.session_state["output"] = make_webpage(
                    markdown_content=st.session_state["md_output"],
                    flashcards=st.session_state["flashcard_output"],
                    encoded_pdf=st.session_state["raw_pdf"],
                    page_range=pages,
                )

            elif edit_what == "Flashcards":
                editor = worker("edit_flashcard", cookies=st.session_state["cookies"])
                editor_chain = editor.get_chain()
                output = editor_chain.invoke(
                    {
                        "request": usr_suggestion,
                        "flashcards": st.session_state["flashcard_output"],
                    }
                )
                st.session_state["flashcard_output"] = output.content
                st.session_state["output"] = make_webpage(
                    markdown_content=st.session_state["md_output"],
                    flashcards=st.session_state["flashcard_output"],
                    encoded_pdf=st.session_state["raw_pdf"],
                    page_range=pages,
                )

            st.rerun()


if __name__ == "__main__":
    main()
