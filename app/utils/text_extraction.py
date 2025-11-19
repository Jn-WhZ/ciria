from pypdf import PdfReader
from docx import Document

def clean_text(text):
    if not text:
        return ""
    # Remove NULL chars that break Postgres
    return text.replace("\x00", "")

def extract_text_from_pdf(upload_file):
    reader = PdfReader(upload_file.file)
    return "\n".join([p.extract_text() or "" for p in reader.pages])

def extract_text_from_docx(upload_file):
    document = Document(upload_file.file)
    return "\n".join([p.text for p in document.paragraphs])

def extract_text_from_plain(upload_file):
    return upload_file.file.read().decode("utf-8")

def extract_text(upload_file):
    filename = upload_file.filename.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(upload_file)

    if filename.endswith(".docx"):
        return extract_text_from_docx(upload_file)

    return clean_text(extract_text_from_plain(upload_file))
