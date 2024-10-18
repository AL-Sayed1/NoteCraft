import streamlit as st
import os
import io
import pdf_handler
from llm_worker import worker
import csv


def display_flashcards(flashcards_data):
    headers = [
        "question",
        "questions",
        "answer",
        "answers",
        "term",
        "terms",
        "definition",
        "definitions",
    ]

    if not flashcards_data:
        st.error("Error Generating Flashcards, No Flashcards generated.")
        return

    if (
        flashcards_data[0][0].strip().lower() in headers
        and flashcards_data[0][1].strip().lower() in headers
    ):
        flashcards_data = flashcards_data[1:]

    st.session_state.questions = [row[0] for row in flashcards_data if len(row) > 1]
    st.session_state.answers = [row[1] for row in flashcards_data if len(row) > 1]

    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    col1, col2, col3 = st.columns(3, gap="small")
    if col1.button("Previous Question"):
        if st.session_state.current_question_index > 0:
            st.session_state.current_question_index -= 1
            st.session_state.show_answer = False
        else:
            st.warning("You are at the first question.")

    if col2.button("Show Answer"):
        st.session_state.show_answer = True

    st.write(f"Total Flashcards {len(st.session_state.questions)}.")

    if col3.button("Next Question"):
        if (
            st.session_state.current_question_index
            < len(st.session_state.questions) - 1
        ):
            st.session_state.current_question_index += 1
            st.session_state.show_answer = False
        else:
            st.warning("You have reached the last question.")

    question = st.session_state.questions[st.session_state.current_question_index]
    st.write(f"Question {st.session_state.current_question_index + 1}: {question}")

    if st.session_state.show_answer:
        answer = st.session_state.answers[st.session_state.current_question_index]
        st.write(f"Answer: {answer}")


def main():
    st.header("NoteCraft AI - Flashcards Generator")

    with st.sidebar:
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
        flashcard_range = " to ".join(map(str, flashcard_range))

        st.subheader("Your Document")

        process = st.button("Process")

    if st.session_state["file"]:
        file_extension = os.path.splitext(st.session_state["file"].name)[1].lower()
        if file_extension != ".pdf" and file_extension != ".csv":
            st.error("The file is not a valid PDF file nor a CSV file.")
            st.stop()
        elif file_extension == ".csv":
            flashcards_io = io.StringIO(
                st.session_state["file"].getvalue().decode("utf-8")
            )
            try:
                flashcards_reader = csv.reader(flashcards_io, delimiter="\t")
                flashcards_data = list(flashcards_reader)
            except csv.Error:
                st.error(
                    "There was an error generating the flashcards, please try again."
                )
                st.write(st.session_state["flashcard_output"])
                st.stop()
            display_flashcards(flashcards_data)
        elif file_extension == ".pdf":
            max_pages = pdf_handler.page_count(st.session_state["file"])
            if max_pages != 1:
                with st.sidebar:
                    pages = st.slider(
                        "Select the pages to generate flashcards from: ",
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
                        llm_worker = worker(
                            task=flashcard_type, cookies=st.session_state["cookies"]
                        )
                        chain = llm_worker.get_chain()
                    except KeyError:
                        st.error(f"The API key is not set.")
                        st.stop()
                    st.session_state.raw_text = pdf_handler.get_pdf_text(
                        st.session_state["file"], page_range=pages
                    )
                    output = chain.invoke(
                        {
                            "transcript": st.session_state.raw_text,
                            "flashcard_range": flashcard_range,
                        }
                    )
                    st.session_state["f_output"] = (
                        output
                        if st.session_state["cookies"]["model"] == "Gemini-1.5"
                        else output.content
                    )

        if "f_output" in st.session_state:
            flashcards_io = io.StringIO(st.session_state["f_output"])
            try:
                flashcards_reader = csv.reader(flashcards_io, delimiter="\t")
                flashcards_data = list(flashcards_reader)
            except csv.Error:
                st.error(
                    "There was an error generating the flashcards, please try again."
                )
                st.write(st.session_state["flashcard_output"])
                st.stop()
            display_flashcards(flashcards_data)

            pdf_name = os.path.splitext(st.session_state["file"].name)[0]

            with st.sidebar:
                st.download_button(
                    label=f"Download flashcards as .csv",
                    data=st.session_state["f_output"],
                    file_name=f"{pdf_name}.csv",
                    mime="text/csv",
                )
                st.markdown(
                    """
                <style>
                    .stTextInput {
                    position: fixed;
                    bottom: 20px;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )

            usr_suggestion = st.text_input(
                label=" ", placeholder="Edit the flashcards so that..."
            )
            if usr_suggestion:
                editor = worker(
                    task="edit_flashcard", cookies=st.session_state["cookies"]
                )
                editor_chain = editor.get_chain()
                output = editor_chain.invoke(
                    {
                        "request": usr_suggestion,
                        "flashcards": st.session_state["f_output"],
                    }
                )
                st.session_state["f_output"] = (
                    output
                    if st.session_state["cookies"]["model"] == "Gemini-1.5"
                    else output.content
                )
                st.rerun()


if __name__ == "__main__":
    main()
