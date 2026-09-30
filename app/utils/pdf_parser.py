import pdfplumber
from pathlib import Path


class PDFParser:
    """
    Responsible for extracting raw text from PDF files.

    This class does NOT perform any semantic understanding,
    section detection, or criteria extraction.
    """

    def parse_uploaded_file(self, uploaded_file) -> str:
        """
        Extract text from a Streamlit UploadedFile object.
        """
        pages_text = []

        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"\n\n--- Page {i + 1} ---\n\n{text}")

        if not pages_text:
            raise ValueError("No extractable text found in uploaded PDF")

        return "\n".join(pages_text)