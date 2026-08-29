import pytest
import io
from backend.resume_parser import ResumeParser

def test_resume_parser_no_file():
    """Test parser throws ValueError when no file is passed"""
    with pytest.raises(ValueError, match="No file provided"):
        ResumeParser.extract_text(None)

def test_resume_parser_invalid_pdf():
    """Test parser handles invalid PDF file bytes gracefully"""
    invalid_pdf = io.BytesIO(b"this is not a valid PDF format string content")
    with pytest.raises(Exception) as exc_info:
        ResumeParser.extract_text(invalid_pdf)
    assert "Failed to parse PDF resume" in str(exc_info.value)
