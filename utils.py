import streamlit as st
from os import environ
from streamlit_cookies_manager import EncryptedCookieManager
import csv
import re
from pdf2image import convert_from_bytes
import pytesseract
from PyPDF2 import PdfReader


def universal_setup(page_title="Home", page_icon="📝", upload_file_types=[]):
    st.set_page_config(
        page_title=f"NoteCraft AI - {page_title}", page_icon=page_icon, layout="wide"
    )
    hide_button_style = """
    <style>
    .e16jpq800, .ef3psqc6 {
        display: none;
    }
    </style>
"""
    if page_title and page_title != "Home":
        st.header(f"NoteCraft AI - {page_title}")
    st.markdown(hide_button_style, unsafe_allow_html=True)

    st.session_state["cookies"] = EncryptedCookieManager(
        prefix=environ.get("COOKIES_PREFIX"),
        password=environ.get("COOKIES_PASSWORD"),
    )
    if upload_file_types:
        st.session_state["file"] = st.sidebar.file_uploader(
            "upload your file", type=upload_file_types
        )


from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import re
from duckduckgo_search import DDGS
from langchain_community.chat_models import ChatOpenAI
import base64
import requests


class LLMAgent:
    def __init__(self, cookies, task="note"):
        self.cookies = cookies
        self.model = self.cookies["model"] if "model" in self.cookies else None
        self.llm = self._initialize_llm()
        self.task = task

    def _initialize_llm(self):
        if self.model == "Gemini-1.5":
            llm = GoogleGenerativeAI(
                model="gemini-1.5-pro",
                api_key=self.cookies["GOOGLE_API_KEY"],
            )
        elif self.model == "GPT-4o-mini":
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=self.cookies["OPENAI_API_KEY"],
            )
        return llm

    def _create_prompt(self):
        if self.task == "note":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are a student writing notes from this transcript, Make sections headers, include all the main ideas in bullets and sub-bullets or in tables or images. Do not include unimportant information such as page numbers, teacher name, etc... Add information that is not in the provided transcript that will help the student better understand the subject. Try to make it clear and easy to understand as possible. Output in Markdown text formatting. To add images use this formatting: <<Write the description of image here>>
                        Do it in {word_range} words.""",
                    ),
                    ("user", "{transcript}"),
                ]
            )
        elif self.task == "edit_note":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """ you are tasked to edit this note:
                        {note}.
                        """,
                    ),
                    (
                        "user",
                        "{request}\nOutput in Markdown formatting. to add images use this formatting: <<Write the description of image here>>",
                    ),
                ]
            )
        elif self.task == "edit_flashcard":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """ You are tasked to make an edit to these flashcards:
                        {flashcards}.
                        """,
                    ),
                    (
                        "user",
                        "{request}\nOutput in the same csv formate with '\t' as the seperator. each row should contain 2 columns: Question \t Answer. only return the csv data without any other information.",
                    ),
                ]
            )
        elif self.task == "Term --> Definition":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are tasked with creating flashcards that will help students learn the important terms, proper nouns and concepts in this note. Only make flashcards directly related to the main idea of the note, include as much detail as possible in each flashcard, returning it in a CSV formate with '\t' as the seperator. each row should include 2 columns: Term \t Definition. make exactly from {flashcard_range} flashcards. only return the csv data without any other information.",
                    ),
                    ("user", "{transcript}"),
                ]
            )
        elif self.task == "Question --> Answer":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are tasked with creating a mock test that will help students learn and understand concepts in this note. Only make questions directly related to the main idea of the note, You should include all these question types: fill in the blank, essay questions, short answer questions and True or False. return the questions and answers in a CSV formate with '\t' as the seperator. each row should include 2 columns: question \t answer. make exactly from {flashcard_range} Questions, Make sure to not generate less or more than the given amount or you will be punished. only return the csv data without any other information.",
                    ),
                    ("user", "{transcript}"),
                ]
            )
        return prompt

    def get_chain(self):
        prompt = self._create_prompt()
        chain = prompt | self.llm
        return chain


def md_image_format(md, encoded=False):
    def replace_with_image(match):
        description = match.group(1).strip()
        results = ddgs.images(keywords=description, max_results=5)
        for result in results:
            image_url = result["image"]
            if encoded:
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                    image_data = response.content
                    image_format = image_url.split(".")[-1]
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    return f"![{description}](data:image/{image_format};base64,{base64_image})"
                except requests.RequestException as e:
                    continue
            else:
                return f"![{description}]({image_url})"
        return "\n"

    pattern = r"<<\s*(.*?)\s*>>"
    ddgs = DDGS()
    modified_md = re.sub(pattern, replace_with_image, md, flags=re.DOTALL)
    return modified_md


def get_pdf_text(pdf, page_range: tuple, format_text=True):
    text = ""
    try:
        pdf_reader = PdfReader(pdf)
    except:
        return "There was a problem reading the pdf, please try."

    if page_range is None:
        first_page = 1
        last_page = len(pdf_reader.pages)
    else:
        first_page, last_page = page_range

    images = convert_from_bytes(
        pdf.getvalue(), first_page=first_page, last_page=last_page
    )

    for page_num, image in enumerate(images, start=first_page):
        image_text = pytesseract.image_to_string(image)
        if image_text.strip():
            text += f"PAGE {page_num}: {image_text}"

    if format_text:
        text = re.sub(r"[\s+\n]", " ", text)
        text = re.sub(r"\f", "", text)

    return text


def page_count(pdf):
    try:
        pdf_reader = PdfReader(pdf)
        return len(pdf_reader.pages)
    except:
        return "Error: EOF marker not found in the PDF file."


def clean_flashcards(flashcards):
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
        flashcards = flashcards[len("```csv") :]
    elif flashcards.startswith("``` csv"):
        flashcards = flashcards[len("``` csv") :]
    if flashcards.endswith("```"):
        flashcards = flashcards[: -len("```")]
    flashcards = flashcards.replace("`", r"\`")

    return flashcards.strip()


def display_flashcards(flashcards):
    if not flashcards:
        st.error("Error Generating Flashcards, No Flashcards generated.")
        return

    flashcards = clean_flashcards(flashcards)
    try:
        flashcards_reader = csv.reader(flashcards.splitlines(), delimiter="\t")
        flashcards_data = list(flashcards_reader)
    except csv.Error:
        st.error("There was an error generating the flashcards, please try again.")
        st.stop()

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
