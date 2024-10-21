import streamlit as st
from dotenv import load_dotenv
from utils import universal_setup



def main():
    universal_setup(page_title="Home", page_icon="🏠")
    html_content = r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NoteCraft</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }
            .container {
                text-align: center;
                padding: 50px;
            }
            .header {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .description {
                font-size: 1.2em;
                margin-bottom: 40px;
            }
            .info-section {
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }
            .info-box {
                padding: 20px;
                border: 2px solid #000;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.3s;
                width: 200px;
                text-align: left;
            }
            .info-box:hover {
                transform: scale(1.1);
            }
            .info-title {
                font-size: 1.5em;
                margin-bottom: 10px;
            }
            .info-content {
                font-size: 1em;
            }
            .more-info {
                margin-top: 40px;
                font-size: 1.2em;
            }
            .more-info div {
                margin-bottom: 20px;
                cursor: pointer;
                transition: color 0.3s;
            }
            .more-info div:hover {
                color: #007BFF;
            }
            .more-info a {
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .studykit-section {
                margin-top: 50px;
                padding: 20px;
                border: 2px solid #000;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            .studykit-title {
                font-size: 2em;
                margin-bottom: 20px;
            }
            .studykit-content {
                font-size: 1.2em;
                text-align: left;
            }
            .feature-section {
                margin-top: 50px;
                padding: 20px;
                border: 2px solid #000;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            .feature-title {
                font-size: 2em;
                margin-bottom: 20px;
            }
            .feature-content {
                font-size: 1.2em;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">NoteCraft, Your Study Companion, Powered by AI</div>
            <div class="description">
                NoteCraft is an AI-powered tool that can answer your questions, generates notes, and flashcards from uploaded PDFs. <br>
                Enhance your learning experience with automatically generated study aids.
            </div>
            <div class="info-section">
                <div class="info-box">
                    <div class="info-title">AI-Powered</div>
                    <div class="info-content">Leverage the power of AI to create accurate and concise notes.</div>
                </div>
                <div class="info-box">
                    <div class="info-title">Easy to Use</div>
                    <div class="info-content">Simply upload your PDF and let NoteCraft do the rest.</div>
                </div>
                <div class="info-box">
                    <div class="info-title">Customizable</div>
                    <div class="info-content">Tailor the generated notes and flashcards to your needs.</div>
                </div>
                <div class="info-box">
                    <div class="info-title">Save Time</div>
                    <div class="info-content">Spend less time making notes and more time studying.</div>
                </div>
            </div>
            <div class="feature-section">
                <div class="feature-title">Note Generator</div>
                <div class="feature-content">
                    Upload a PDF and generate a summarized note of the content. This feature helps you quickly grasp the key points of your document.
                </div>
            </div>
            <div class="feature-section">
                <div class="feature-title">Flashcard Generator</div>
                <div class="feature-content">
                    Upload a PDF and generate flashcards based on the content. This feature aids in quick revision and better retention of information.
                </div>
            </div>
            <div class="studykit-section">
                <div class="studykit-title">NoteCraft StudyKit</div>
                <div class="studykit-content">
                    Create an entire interactive document in HTML which includes:
                    <ul>
                        <li>Table of Contents</li>
                        <li>Notes</li>
                        <li>Questions</li>
                        <li>Reference PDF</li>
                    </ul>
                    Enhance your study sessions with a comprehensive and interactive study kit.
                </div>
            </div>
            <div class="more-info">
                <div>Crafted by Sayed Hashim</div>
                <div><a href="https://github.com/AL-Sayed1/NoteCraft" target="_blank">View github code</a></div>
            </div>
        </div>
    </body>
    </html>
    """
    # Streamlit rendering
    st.markdown(html_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
