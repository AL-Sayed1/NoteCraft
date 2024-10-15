import re
from pdf2image import convert_from_bytes
import pytesseract
from PyPDF2 import PdfReader


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
