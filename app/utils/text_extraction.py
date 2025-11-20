import io
from PyPDF2 import PdfReader
import docx
import mimetypes

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from raw bytes downloaded from Supabase.
    """

    # Convert to BytesIO
    stream = io.BytesIO(file_bytes)

    # Detect file type from extension
    ext = filename.lower().split(".")[-1]

    # -------------------------------
    # PDF
    # -------------------------------
    if ext == "pdf":
        try:
            reader = PdfReader(stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")

    # -------------------------------
    # DOCX
    # -------------------------------
    if ext == "docx":
        try:
            doc = docx.Document(stream)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")

    # -------------------------------
    # TXT
    # -------------------------------
    if ext in ["txt", "md"]:
        try:
            return stream.read().decode("utf-8", errors="ignore")
        except Exception:
            return stream.read().decode("latin-1", errors="ignore")

    # -------------------------------
    # Unsupported type
    # -------------------------------
    raise Exception(f"Unsupported file type: {ext}")
