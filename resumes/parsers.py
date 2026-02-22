import pdfplumber
from docx import Document


def extract_text_from_resume(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        return _extract_pdf_text(file_path)
    if file_path.lower().endswith(".docx"):
        return _extract_docx_text(file_path)
    return ""


def _extract_pdf_text(file_path: str) -> str:
    content = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            content.append(page.extract_text() or "")
    return "\n".join(content).strip()


def _extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs).strip()
