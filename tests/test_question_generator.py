import pytest
from unittest.mock import MagicMock
from backend.groq_client import GroqClient
from backend.question_generator import QuestionGenerator

def test_prompt_creation():
    """Test that build_prompt correctly formats the LLM inputs"""
    client = GroqClient(api_key="gsk_test")
    
    # 1. Test basic prompt parameter inclusion
    prompt = client._build_prompt(
        job_role="Java Developer",
        experience_level="Fresher",
        difficulty="Medium",
        topic_focus="OOP",
        num_questions=3
    )
    assert "Java Developer" in prompt
    assert "Fresher" in prompt
    assert "Medium" in prompt
    assert "OOP" in prompt
    assert "3" in prompt
    
    # 2. Test prompt with resume context inclusion
    prompt_with_resume = client._build_prompt(
        job_role="Python Developer",
        experience_level="2 Years",
        difficulty="Hard",
        topic_focus="DBMS",
        num_questions=5,
        resume_text="Worked on Flask and PostgreSQL project."
    )
    assert "Flask" in prompt_with_resume
    assert "PostgreSQL" in prompt_with_resume


def test_parse_response_valid():
    """Test that valid structured JSON string is successfully parsed and normalized"""
    client = GroqClient(api_key="gsk_test")
    valid_json = """
    {
      "questions": [
        {
          "question": "What is OOP?",
          "answer": "Object-oriented programming...",
          "explanation": "Explanation here",
          "difficulty": "Medium",
          "topic": "OOP",
          "tips": "Understand encapsulation",
          "common_mistakes": "Confusing abstraction with interfaces",
          "follow_up_question": "What is inheritence?"
        }
      ]
    }
    """
    result = client._parse_response(valid_json)
    assert "questions" in result
    assert len(result["questions"]) == 1
    assert result["questions"][0]["question"] == "What is OOP?"
    assert result["questions"][0]["difficulty"] == "Medium"
    # Ensure singular string fields are successfully normalized to lists for the app
    assert result["questions"][0]["tips"] == ["Understand encapsulation"]
    assert result["questions"][0]["common_mistakes"] == ["Confusing abstraction with interfaces"]
    assert result["questions"][0]["follow_up_questions"] == ["What is inheritence?"]


def test_parse_response_invalid_json_fallback():
    """Test that malformed JSON doesn't crash the parser and falls back gracefully"""
    client = GroqClient(api_key="gsk_test")
    invalid_json = "This is not a JSON. Just normal conversational response from LLM."
    result = client._parse_response(invalid_json)
    assert "questions" in result
    assert len(result["questions"]) > 0
    assert "question" in result["questions"][0]


def test_question_generator_mocked_run():
    """Test generation workflow from end-to-end using a mocked API client"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
    {
      "questions": [
        {
          "question": "What is Flask?",
          "answer": "A Python microframework...",
          "explanation": "Uses WSGI and Jinja",
          "difficulty": "Easy",
          "topic": "Flask",
          "tips": "Focus on simplicity",
          "common_mistakes": "Overcomplicating layouts",
          "follow_up_question": "What is Django?"
        }
      ]
    }
    """
    
    # Initialize real client but replace external network call object with mock
    client = GroqClient(api_key="gsk_test")
    client.client = mock_client
    mock_client.chat.completions.create.return_value = mock_response
    
    generator = QuestionGenerator("gsk_test")
    generator.groq_client = client
    
    result = generator.generate(
        job_role="Python Developer",
        experience_level="Fresher",
        difficulty="Easy",
        topic_focus="Flask",
        num_questions=1
    )
    
    assert "error" not in result
    assert len(result["questions"]) == 1
    assert result["questions"][0]["question"] == "What is Flask?"
    assert result["metadata"]["job_role"] == "Python Developer"
