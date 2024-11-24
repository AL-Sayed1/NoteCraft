import streamlit as st
from utils import universal_setup


def main():
    universal_setup(page_icon="🏠")
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
                display: inline-block;
            }
            .more-info div {
                margin-bottom: 20px;
                cursor: pointer;
                transition: color 0.3s;
            }
            .more-info div:hover {
                color: #ff4b4b;
            }
            .more-info a {
                text-decoration: none;
                color: inherit;
                display: inline-block;
            }
            .feature-link {
                text-decoration: none;
                color: #31333f !important;
                display: block;
                border: 2px solid #000;
                border-radius: 10px;
                background-color: #f9f9f9;
                transition: border-color 0.3s, color 0.3s, box-shadow 0.3s;
                margin-top: 50px;
                padding: 20px;
            }
            .feature-link:hover {
                color: #ff4b4b;
                border-color: #ff4b4b;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                text-decoration: none;
            }
            .feature-link:hover .feature-title, .feature-link:hover .feature-content {
                color: #ff4b4b;
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
                NoteCraft is an AI-powered tool that can generates notes, and flashcards from any PDF! <br>
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
                    <div class="info-content">Spend less time making notes and flashcards and more time studying.</div>
                </div>
            </div>
            <a href="/Note_generator" class="feature-link">
                <div class="feature-title">Note Generator</div>
                <div class="feature-content">
                    <p>Generate concise notes from your PDF content using AI! Just follow these simple steps:</p>
                    <ul>
                        <li>Upload your PDF</li>
                        <li>Select the desired note length</li>
                        <li>Press "Process" and let NoteCraft handle the rest!</li>
                    </ul>
                </div>
            </a>
            <a href="/Flashcard_Generator" class="feature-link">
                <div class="feature-title">Flashcard Generator</div>
                <div class="feature-content">
                    Generate flashcards from the content of your PDF using AI!
                    you can choose:
                    <ul>
                        <li>Number of flashcards</li>
                        <li>Select the flashcard type:
                            <ul>
                                <li>Question | Answer</li>
                                <li>Term | Definition</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </a>
            <a href="/NoteCraft_study_kit" class="feature-link">
                <div class="feature-title">NoteCraft StudyKit</div>
                <div class="feature-content">
                    Generates an entire interactive document which includes:
                    <ul>
                        <li>Table of Contents</li>
                        <li>AI-Generated Notes</li>
                        <li>Questions</li>
                        <li>Reference PDF</li>
                        <li>User Notes</li>
                        <li>Pomodoro Timer</li>
                    </ul>
                    All in one place!
                </div>
            </a>
            <div class="more-info">
                <div>Crafted by Sayed Hashim</div>
                <div><a href="https://github.com/AL-Sayed1/NoteCraft" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16">
  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/></svg> View github code</a></div>
            </div>
        </div>
    </body>
    </html>
    """

    st.markdown(html_content, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
