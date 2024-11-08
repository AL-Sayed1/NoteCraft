import streamlit as st
from os import environ
from streamlit_cookies_manager import EncryptedCookieManager
import csv
import re
from pdf2image import convert_from_bytes
import pytesseract
from PyPDF2 import PdfReader
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from duckduckgo_search import DDGS
from langchain_community.chat_models import ChatOpenAI
import base64
import requests
from google.api_core.exceptions import ResourceExhausted

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



class LLMAgent:
    def __init__(self, cookies):
        self.cookies = cookies
        self.model = self.cookies["model"] if "model" in self.cookies else None
        self.llm = self._initialize_llm()

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

    def _get_chain(self, task):
        task_prompts = {
            "note": ChatPromptTemplate.from_messages([
                ("system", """You are a student writing notes from this transcript, Make sections headers, include all the main ideas in bullets and sub-bullets or in tables or images. Do not include unimportant information such as page numbers, teacher name, etc... Add information that is not in the provided transcript that will help the student better understand the subject. Try to make it clear and easy to understand as possible. Output in Markdown text formatting. To add images use this formatting: <<Write the description of image here>> Do it in {word_range} words."""),
                ("user", "{transcript}"),
            ]),

            "edit_note": ChatPromptTemplate.from_messages([
                ("system", """ you are tasked to edit this note: {text}."""),
                ("user", "{request}\nOutput in Markdown formatting. to add images use this formatting: <<Write the description of image here>>"),
            ]),
            "page_note": ChatPromptTemplate.from_messages([
                ("system", "Write a brief summary of the following without adding any extra information: {transcript}."),
            ]),
            "final_note": ChatPromptTemplate.from_messages([
                ("system", """Combine the given summaries, include all main ideas in bullets, sub-bullets, tables, or images. Add additional information to help the student better understand the subject. Output in Markdown formatting. To add images use: <<Image description here>>. Do it in {word_range} words."""),
                ("user", "Summaries: {summaries}"),
            ]),
            "edit_flashcard": ChatPromptTemplate.from_messages([
                ("system", """ You are tasked to make an edit to these flashcards: {text}."""),
                ("user", "{request}\nOutput in the same csv formate with '\t' as the seperator. each row should contain 2 columns: Question \t Answer. only return the csv data without any other information."),
            ]),
            "Term --> Definition": ChatPromptTemplate.from_messages([
                ("system", "You are tasked with creating flashcards that will help students learn the important terms, proper nouns and concepts in this note. Only make flashcards directly related to the main idea of the note, include as much detail as possible in each flashcard, returning it in a CSV formate with '\t' as the seperator. each row should include 2 columns: Term \t Definition. make exactly from {flashcard_range} flashcards. only return the csv data without any other information."),
                ("user", "{transcript}"),
            ]),
            "Question --> Answer": ChatPromptTemplate.from_messages([
                ("system", "You are tasked with creating a mock test that will help students learn and understand concepts in this note. Only make questions directly related to the main idea of the note, You should include all these question types: fill in the blank, essay questions, short answer questions and True or False. return the questions and answers in a CSV formate with '\t' as the seperator. each row should include 2 columns: question \t answer. make exactly from {flashcard_range} Questions, Make sure to not generate less or more than the given amount or you will be punished. only return the csv data without any other information."),
                ("user", "{transcript}"),
            ]),
        }
        return task_prompts.get(task) | self.llm
    
    def get_note(self, transcript, word_range):
        if st.session_state["cookies"]["pageWise"] == "True":
            page_notes_chain = self._get_chain("page_note")
            final_note_chain = self._get_chain("final_note")
            try:
                summaries = "\n".join(
                (page_notes_chain.invoke({"transcript": doc})
                if st.session_state["cookies"]["model"] == "Gemini-1.5"
                else page_notes_chain.invoke({"transcript": doc}).content)
                for doc in transcript
            )
                self.note = final_note_chain.invoke({"summaries": summaries, "word_range": word_range})
            except ResourceExhausted:
                st.error("API Exhausted, if you are using the free version of the API, you may have reached the limit.\nTry again later.\nIf PageWise is enabled, try disabling it.")
        else:
            note_prompt = self._get_chain(self.task)
            try:
                self.note = note_prompt.invoke({"transcript": transcript, "word_range": word_range})
            except ResourceExhausted:
                st.error("API Exhausted, if you are using the free version of the API, you may have reached the limit.\nTry again later.\nIf PageWise is enabled, try disabling it.")
        return self.note

    def get_flashcards(self, flashcard_range, task="Term --> Definition", transcript=None):
        if st.session_state["cookies"]["pageWise"] == "True":
            page_notes_chain = self._get_chain("page_note")
            final_flashcard_chain = self._get_chain(task)
            try:
                summaries = "\n".join(
                (page_notes_chain.invoke({"transcript": doc})
                if st.session_state["cookies"]["model"] == "Gemini-1.5"
                else page_notes_chain.invoke({"transcript": doc}).content)
                for doc in transcript
                )
                self.flashcards = final_flashcard_chain.invoke({"transcript": summaries, "flashcard_range": flashcard_range})
            except ResourceExhausted:
                st.error("API Exhausted, if you are using the free version of the API, you may have reached the limit.\nTry again later.\nIf PageWise is enabled, try disabling it.")
        else:
            flashcard_chain = self._get_chain(task)
            if transcript is None:
                transcript = self.note
            try:
                self.flashcards = flashcard_chain.invoke({"transcript": transcript, "flashcard_range": flashcard_range})
            except ResourceExhausted:
                st.error("API Exhausted, if you are using the free version of the API, you may have reached the limit.\nTry again later.\nIf PageWise is enabled, try disabling it.")
        return self.flashcards
    
    def edit(self, task, request, text):
        edit_chain = self._get_chain(task)
        try:
            return edit_chain.invoke({"request": request, "text": text})
        except ResourceExhausted:
                st.error("API Exhausted, if you are using the free version of the API, you may have reached the limit.\nTry again later.\nIf PageWise is enabled, try disabling it.")

            

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

def get_base64_encoded_pdf(file):
    file.seek(0)
    pdf_content = file.read()
    encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")
    return encoded_pdf

def get_pdf_text(pdf, page_range: tuple):
    try:
        pdf_reader = PdfReader(pdf)
    except Exception as e:
        return f"There was a problem reading the pdf: {str(e)}"

    if page_range is None:
        first_page = 1
        last_page = len(pdf_reader.pages)
    else:
        first_page, last_page = page_range

    images = convert_from_bytes(
        pdf.getvalue(), first_page=first_page, last_page=last_page
    )

    page_texts = []
    for image in images:
        image_text = pytesseract.image_to_string(image)
        if image_text.strip():
            page_texts.append(image_text)

    if st.session_state["cookies"]["pageWise"] == "True":
        final_texts = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=10,
            separators=[".", "!", "?", "\n"],
        )

        idx = 0
        while idx < len(page_texts):
            page = page_texts[idx]
            if len(page.split()) < 75 and idx + 1 < len(page_texts):
                page += " " + page_texts[idx + 1]
                idx += 1
            final_texts.extend(text_splitter.split_text(page))
            idx += 1
        
        return final_texts
    else:
        return ' '.join(page_texts).strip()


def page_count(pdf):
    try:
        pdf_reader = PdfReader(pdf)
        return len(pdf_reader.pages)
    except:
        return "Error: EOF marker not found in the PDF file."


def clean_flashcards(flashcards):
    unwanted_headers_col1 = {"question", "questions", "term", "terms"}
    unwanted_headers_col2 = {"answer", "answers", "definition", "definitions"}
    
    flashcards = re.sub(r"^\s*```(?:csv\s*)?", "", flashcards, flags=re.IGNORECASE)
    flashcards = re.sub(r"```\s*$", "", flashcards, flags=re.IGNORECASE)

    pattern = re.compile(r"^\s*(\w+)\s*\t\s*(\w+)\s*\n", re.IGNORECASE)
    match = pattern.match(flashcards)

    if match:
        col1, col2 = match.groups()
        if col1.lower() in unwanted_headers_col1 and col2.lower() in unwanted_headers_col2:
            flashcards = flashcards[match.end():]

    
    flashcards = re.sub(r"\t+", "\t", flashcards)

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

def parse_studkit(content):
    note = re.search(r'note=`\^(.*?)`\^', content, re.DOTALL).group(1)
    flashcards = re.search(r'flashcards=`\^(.*?)`\^', content, re.DOTALL).group(1)
    return note, flashcards