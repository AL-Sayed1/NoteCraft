import streamlit as st
import os
import utils


def main():
    utils.universal_setup(
        page_title="Flashcards Generator",
        page_icon="📄",
        upload_file_types=["pdf", "csv"],
        worker=True,
        yt_upload=True,
    )
    if "f_output" not in st.session_state:
        st.markdown(
            """
        ### How to Generate Flashcards
        1. **Upload your PDF**: Use the file uploader in the sidebar to upload your document.
        2. **Select the number of flashcards**: Adjust the slider to set the desired flashcard range.
        3. **Select the flashcards type**: Choose either 'Term --> Definition' or 'Question --> Answer' flashcards.
        4. **Choose pages (for PDFs)**: once you uploaded a PDF, select the pages you want to generate flashcards from.
        5. **Click 'Process'**: Hit the 'Process' button to generate your flashcards.
        6. **Download or Edit**: Once the flashcards are generated, you can download them as a csv file or edit them using the chat input.
        """
        )
    with st.sidebar:
        flashcard_type = st.radio(
            "Flashcard Type",
            ["Term --> Definition", "Question --> Answer", "MCQ --> Answer"],
        )
        flashcard_range = st.slider(
            "Select how many flashcards do you want",
            value=(5, 20),
            step=5,
            min_value=5,
            max_value=60,
        )

        process = st.button("Process", use_container_width=True)


    if st.session_state["upload"][0] == "file" and st.session_state["upload"][1] is not None:
        st.session_state["file_name"], file_extension = os.path.splitext(st.session_state["upload"][1].name)
        file_extension = file_extension.lower()

        if file_extension != ".pdf" and file_extension != ".csv":
            st.error("The file is not a valid PDF file nor a CSV file.")
            st.stop()
        elif file_extension == ".csv":
            utils.display_flashcards(
                st.session_state["upload"][1].getvalue().decode("utf-8")
            )
        elif file_extension == ".pdf":
            max_pages = utils.page_count(st.session_state["upload"][1])
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
            if st.session_state["upload"][0] == "file" and st.session_state["upload"][1] is not None:
                st.session_state.raw_text = utils.get_pdf_text(
                    st.session_state["upload"][1], page_range=pages
                )
            elif st.session_state["upload"][0] == "youtube" and st.session_state["upload"][1] is not None:
                st.session_state.raw_text = utils.fetch_transcript(st.session_state["upload"][1])
                st.session_state["file_name"] = "NoteCraft Video Notes"
            try:
                output = st.session_state["worker"].get_flashcards(
                    flashcard_range=flashcard_range,
                    task=flashcard_type,
                    transcript=st.session_state.raw_text,
                )
            except (KeyError, UnboundLocalError):
                st.error(
                    "You don't have access to the selected model. [Get access here](/get_access)."
                )
                st.stop()
            st.session_state["f_output"] = (
                output
                if st.session_state["cookies"]["model"] == "Gemini-1.5"
                else output.content
            )

    if "f_output" in st.session_state:
        utils.display_flashcards(st.session_state["f_output"])
        st.download_button(
            label=f"Download flashcards as .csv",
            data=st.session_state["f_output"],
            file_name=f"{st.session_state["file_name"]}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            label="Download Paper Flashcards (PDF)",
            data=utils.paper(
                header_text=st.session_state["file_name"],
                flashcards=st.session_state["f_output"],
            ),
            file_name=f"{st.session_state['file_name']} - Flashcards.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


        usr_suggestion = st.chat_input(
            placeholder="Edit the flashcards so that..."
        )
        if usr_suggestion:
            output = st.session_state["worker"].edit(
                task="edit_flashcards",
                request=usr_suggestion,
                text=st.session_state["f_output"],
            )
            st.session_state["f_output"] = (
                output
                if st.session_state["cookies"]["model"] == "Gemini-1.5"
                else output.content
            )
            st.session_state["current_question_index"] = 0
            st.rerun()


if __name__ == "__main__":
    main()
