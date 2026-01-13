"""
PDF Parser for Clinical Trial Protocols
Extracts text from PDF files and provides preprocessing utilities
"""

import PyPDF2
from typing import Optional, Dict, List
import re


class PDFParser:
    """
    Parse PDF files and extract text content
    """
    
    def __init__(self):
        self.text = ""
        self.metadata = {}
        self.page_count = 0
    
    def parse_file(self, file_path: str) -> str:
        """
        Parse a PDF file and return extracted text
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text from all pages
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get metadata
                self.page_count = len(pdf_reader.pages)
                self.metadata = pdf_reader.metadata or {}
                
                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                self.text = "\n\n".join(text_parts)
                return self.text
                
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def parse_uploaded_file(self, uploaded_file) -> str:
        """
        Parse a PDF from Streamlit's UploadedFile object
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Extracted text
        """
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            
            # Get metadata
            self.page_count = len(pdf_reader.pages)
            self.metadata = pdf_reader.metadata or {}
            
            # Extract text
            text_parts = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            self.text = "\n\n".join(text_parts)
            return self.text
            
        except Exception as e:
            raise Exception(f"Error parsing uploaded PDF: {str(e)}")
    
    def clean_text(self, text: Optional[str] = None) -> str:
        """
        Clean extracted text by removing extra whitespace and formatting issues
        
        Args:
            text: Text to clean (uses self.text if not provided)
            
        Returns:
            Cleaned text
        """
        if text is None:
            text = self.text
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix hyphenated words at line breaks
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # Remove page numbers (common pattern: "Page X of Y")
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        
        # Remove common footer patterns
        text = re.sub(r'Confidential.*?(?=\n)', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_sections(self, text: Optional[str] = None) -> Dict[str, str]:
        """
        Attempt to extract major sections from protocol text
        
        Args:
            text: Text to process (uses self.text if not provided)
            
        Returns:
            Dictionary of section titles and their content
        """
        if text is None:
            text = self.text
        
        sections = {}
        
        # Common section patterns in clinical trial protocols
        section_patterns = [
            r'(\d+\.?\d*)\s+(INCLUSION CRITERIA)',
            r'(\d+\.?\d*)\s+(EXCLUSION CRITERIA)',
            r'(\d+\.?\d*)\s+(ELIGIBILITY CRITERIA)',
            r'(\d+\.?\d*)\s+(STUDY OBJECTIVES?)',
            r'(\d+\.?\d*)\s+(STUDY DESIGN)',
            r'(\d+\.?\d*)\s+(ENDPOINTS?)',
            r'(\d+\.?\d*)\s+(OUTCOME MEASURES?)',
            r'(\d+\.?\d*)\s+(PATIENT SELECTION)',
            r'(\d+\.?\d*)\s+(SCHEDULE OF ASSESSMENTS?)',
            r'(\d+\.?\d*)\s+(VISIT SCHEDULE)',
        ]
        
        # Find all section headers
        section_positions = []
        for pattern in section_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                section_num = match.group(1)
                section_title = match.group(2)
                section_positions.append({
                    'start': match.start(),
                    'title': section_title,
                    'number': section_num
                })
        
        # Sort by position
        section_positions.sort(key=lambda x: x['start'])
        
        # Extract content between sections
        for i, section in enumerate(section_positions):
            start = section['start']
            # End is the start of next section, or end of text
            end = section_positions[i + 1]['start'] if i + 1 < len(section_positions) else len(text)
            
            section_content = text[start:end].strip()
            sections[section['title']] = section_content
        
        return sections
    
    def get_metadata_summary(self) -> Dict:
        """
        Get a summary of the PDF metadata
        
        Returns:
            Dictionary with metadata information
        """
        return {
            'page_count': self.page_count,
            'title': self.metadata.get('/Title', 'Unknown'),
            'author': self.metadata.get('/Author', 'Unknown'),
            'creator': self.metadata.get('/Creator', 'Unknown'),
            'producer': self.metadata.get('/Producer', 'Unknown'),
            'creation_date': self.metadata.get('/CreationDate', 'Unknown'),
        }
    
    def estimate_word_count(self, text: Optional[str] = None) -> int:
        """
        Estimate word count in the text
        
        Args:
            text: Text to count (uses self.text if not provided)
            
        Returns:
            Estimated word count
        """
        if text is None:
            text = self.text
        
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def truncate_for_api(self, text: Optional[str] = None, max_tokens: int = 100000) -> str:
        """
        Truncate text to fit within API token limits
        Rough estimate: 1 token ≈ 4 characters
        
        Args:
            text: Text to truncate (uses self.text if not provided)
            max_tokens: Maximum number of tokens
            
        Returns:
            Truncated text
        """
        if text is None:
            text = self.text
        
        max_chars = max_tokens * 4  # Rough approximation
        
        if len(text) <= max_chars:
            return text
        
        # Truncate and add notice
        truncated = text[:max_chars]
        truncated += "\n\n[... Document truncated due to length ...]"
        
        return truncated


def parse_pdf(file_path: str) -> str:
    """
    Convenience function to quickly parse a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Cleaned extracted text
    """
    parser = PDFParser()
    text = parser.parse_file(file_path)
    return parser.clean_text(text)


def parse_uploaded_pdf(uploaded_file) -> str:
    """
    Convenience function to parse a Streamlit uploaded file
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Cleaned extracted text
    """
    parser = PDFParser()
    text = parser.parse_uploaded_file(uploaded_file)
    return parser.clean_text(text)