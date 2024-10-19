from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from os import environ
import re
from duckduckgo_search import DDGS
from langchain_community.chat_models import ChatOpenAI


class worker:
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
        elif self.model == "GPT-4o":
            llm = ChatOpenAI(
                model="gpt-4o",
                api_key=self.cookies["OPENAI_API_KEY"],
            )
        return llm

    def _create_prompt(self):
        if self.task == "note":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are a student writing notes from this transcript, Make sections headers, include all the main ideas in bullets and sub-bullets or in tables or images. Do not include unimportant information such as page numbers, teacher name, etc... Add information that is not in the provided transcript that will help the student better understand the subject. Try to make it clear and easy to understand as possible. Output in only Markdown text formatting. To add images use this formatting: <<Write the description of image here>>
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
                        """ You are tasked to make an edit to this note:
                        {note}.

                        Only use Markdown text formatting in your output, to add images use this formatting: <<Write the description of image here>>""",
                    ),
                    ("user", "{request}"),
                ]
            )
        elif self.task == "edit_flashcard":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """ You are tasked to make an edit to these flashcards:
                        {flashcards}.
                        
                        output in the same csv formate with '\t' as the seperator. each row should contain 2 columns: Question \t Answer. only return the csv data without any other information.""",
                    ),
                    ("user", "{request}"),
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


import re
import base64
import requests
from io import BytesIO


def md_image_format(md, encoded=False):
    def replace_with_image(match):
        description = match.group(1).strip()
        results = ddgs.images(keywords=description, max_results=1)
        if results:
            image_url = results[0]["image"]
            if encoded:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content
                    image_format = image_url.split(".")[-1]
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    return f"![{description}](data:image/{image_format};base64,{base64_image})"
            else:
                return f"![{description}]({image_url})"
        return match.group(0)

    pattern = r"<<\s*(.*?)\s*>>"
    ddgs = DDGS()
    modified_md = re.sub(pattern, replace_with_image, md)
    return modified_md
