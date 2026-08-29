"""
Resume Parser Service using pypdf
"""
import pypdf
from typing import Optional

class ResumeParser:
    """Service to parse resumes (PDF format)"""
    
    @staticmethod
    def extract_text(pdf_file) -> str:
        """
        Extract text content from a PDF file-like object or path
        
        Args:
            pdf_file: File-like object (e.g. BytesIO) or file path
            
        Returns:
            Extracted text content as a string
            
        Raises:
            Exception: If PDF is invalid, empty, or unreadable
        """
        if pdf_file is None:
            raise ValueError("No file provided")
            
        try:
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            cleaned_text = text.strip()
            if not cleaned_text:
                raise ValueError("PDF file is empty or contains no readable text")
                
            return cleaned_text
        except Exception as e:
            raise Exception(f"Failed to parse PDF resume: {str(e)}")
