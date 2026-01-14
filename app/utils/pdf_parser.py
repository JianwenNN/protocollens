import pdfplumber
from pathlib import Path


class PDFParser:
    """
    Responsible for extracting raw text from PDF files.

    This class does NOT perform any semantic understanding,
    section detection, or criteria extraction.
    """

    def parse(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            file_path (str): Path to the PDF file

        Returns:
            str: Raw extracted text with page order preserved

        Raises:
            FileNotFoundError: If PDF does not exist
            ValueError: If no text could be extracted
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        pages_text = []

        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"\n\n--- Page {i + 1} ---\n\n{text}")

        if not pages_text:
            raise ValueError("No extractable text found in PDF")

        return "\n".join(pages_text)

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