# 📝 NoteCraft AI

**NoteCraft AI** is a powerful, free, and open-source tool designed to create study materials (Notes and Flashcards)
---

## 🌟 Features

- AI-powered **note generator**.
- **Flashcard generator** to create study materials for quick revision
- Supports OCR for extracting text from images in PDFs

---

### Note Generator Interface
![Note Generator](screenshots/note_generator.png)

### Flashcard Generator Interface
![Flashcard Generator](screenshots/flashcard_generator.png)

---

## 🚀 Getting Started

### 1. Clone the repository and install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Install `tesseract-ocr` and `poppler` (required for OCR functionality):

For Debian-based systems, run:

```bash
sudo apt install tesseract-ocr poppler-utils
```

### 3. Run the application:

```bash
streamlit run 📝_Note_generator.py
```

---