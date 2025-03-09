import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import utils
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI


def get_conversation_chain(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    text_chunks = text_splitter.split_text(text)

    if st.session_state["cookies"].get("model") == "GPT-4o-mini" and st.session_state[
        "cookies"
    ].get("OPENAI_API_KEY"):
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=st.session_state["cookies"]["OPENAI_API_KEY"],
        )
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=st.session_state["cookies"]["OPENAI_API_KEY"],
        )
    elif st.session_state["cookies"].get("model") == "Gemini-1.5" and st.session_state[
        "cookies"
    ].get("GOOGLE_API_KEY"):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=st.session_state["cookies"]["GOOGLE_API_KEY"],
        )
        llm = GoogleGenerativeAI(
            model="gemini-1.5-pro",
            api_key=st.session_state["cookies"]["GOOGLE_API_KEY"],
        )
    else:
        st.error(
            "You don't have access to the selected model. [Get access here](/get_access)."
        )
        return

    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    prompt = """
    You are a teacher that answers the students questions about the context they provide which is a PDF file, and you will reply in markdown and explain using easy terms, giving examples etc...
                                        
    <context>
    {context}
    </context>
    """

    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, answer the users question."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, vectorstore.as_retriever(), contextualize_q_prompt
    )

    document_chain = create_stuff_documents_chain(llm, qa_prompt)

    conversation_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    return conversation_chain


def handle_user_input(user_prompt):
    chat_history = [
        {"role": msg["role"], "content": str(msg["content"])}
        for msg in st.session_state.chat_history
    ]

    try:
        response = st.session_state.conversation.invoke(
            {"input": user_prompt, "chat_history": chat_history}
        )
    except AttributeError:
        st.chat_message("assistant").write("Please upload a PDF file and press process before you start chatting.")
        return
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    st.session_state.chat_history.append({"role": "ai", "content": response["answer"]})

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "ai":
            with st.chat_message("assistant"):
                if isinstance(msg["content"], dict) and "answer" in msg["content"]:
                    st.write(msg["content"]["answer"])
                else:
                    st.write(msg["content"])


def main():
    utils.universal_setup(
        page_title="Ask My Document", page_icon="🔍", upload_file_types=["pdf", "docx", "pptx"]
    )

    if (
        "conversation" not in st.session_state
        or st.session_state["conversation"] is None
    ):
        st.write(
            """
            This is a chatbot that answers students' questions based on the provided document.

            **How to use**: Just upload a **PDF, Word, or PowerPoint file**, press process, and start asking questions right away!
            """
        )
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if st.sidebar.button("process", use_container_width=True):
        if st.session_state.get("file") is None:
            st.chat_message("assistant").write("Please upload a PDF file first.")
        else:
            try:
                with st.spinner("Processing"):
                    # Extract text from pdf
                    raw_text = utils.get_document_text(
                        st.session_state["file"],
                        page_range=None,
                    )

                    # Get conversation chain
                    st.session_state.conversation = get_conversation_chain(raw_text)
                    st.success("Done! You can now start chatting.")
            except AttributeError:
                st.error("Please upload a valid PDF file.")
                return

    user_input = st.chat_input(placeholder="Ask me anything")
    if user_input:
        handle_user_input(user_input)


if __name__ == "__main__":
    main()
