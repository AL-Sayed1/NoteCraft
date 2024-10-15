import streamlit as st
import os
import pdf_handler
from llm_worker import worker
from llm_worker import md_image_format


def main():
    st.header("NoteCraft AI")

    with st.sidebar:
        word_range = st.slider(
            "Select the word range",
            value=(200, 300),
            step=50,
            min_value=50,
            max_value=1000,
        )
        word_range = " to ".join(map(str, word_range))
        st.subheader("Your Documents")

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
                        llm_worker = worker(cookies=st.session_state["cookies"])
                        chain = llm_worker.get_chain()
                    except KeyError:
                        st.error(f"The API key is not set.")
                        st.stop()
                    raw_text = pdf_handler.get_pdf_text(
                        st.session_state["file"], page_range=pages
                    )
                    output = chain.invoke(
                        {"transcript": raw_text, "word_range": word_range}
                    )
                    st.session_state["output"] = md_image_format(output)
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
            editor = worker("edit_note", cookies=st.session_state["cookies"])
            editor_chain = editor.get_chain()
            output = editor_chain.invoke(
                {"request": usr_suggestion, "note": st.session_state["output"]}
            )
            st.session_state["output"] = md_image_format(output)
            st.rerun()


if __name__ == "__main__":
    main()
