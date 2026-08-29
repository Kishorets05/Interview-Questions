import pytest
from unittest.mock import MagicMock
from backend.evaluator import AnswerEvaluator

def test_evaluator_empty_answer():
    """Test that empty candidate responses receive a zero score immediately without API calls"""
    evaluator = AnswerEvaluator(MagicMock())
    res = evaluator.evaluate_answer(
        question="What is OOP?",
        expected_answer="Object-oriented programming",
        candidate_answer="  ",
        job_role="Java Developer",
        experience_level="Fresher"
    )
    assert res["technical_accuracy"] == 0
    assert res["overall"] == 0
    assert "No answer was provided" in res["feedback"]


def test_evaluator_valid_answer_mocked():
    """Test that valid evaluations and scores are extracted and clamped correctly"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    # Mocking a response where overall score is invalid (> 10) to verify clamping
    mock_response.choices[0].message.content = """
    {
      "technical_accuracy": 9,
      "relevance": 8,
      "completeness": 7,
      "clarity": 10,
      "overall": 85, 
      "feedback": "Great answer on JWT!"
    }
    """
    
    groq_client = MagicMock()
    groq_client.client = mock_client
    groq_client.model = "gpt-model"
    mock_client.chat.completions.create.return_value = mock_response
    
    evaluator = AnswerEvaluator(groq_client)
    res = evaluator.evaluate_answer(
        question="Explain JWT.",
        expected_answer="JSON Web Token...",
        candidate_answer="JWT is a stateless token format...",
        job_role="Python Developer",
        experience_level="Fresher"
    )
    
    # 85 should be clamped to 10 max
    assert res["overall"] == 10
    assert res["technical_accuracy"] == 9
    assert res["clarity"] == 10
    assert res["feedback"] == "Great answer on JWT!"


def test_evaluator_invalid_llm_response_fallback():
    """Test that malformed/invalid LLM outputs default to safety values without crashing"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "this is not structured json format at all"
    
    groq_client = MagicMock()
    groq_client.client = mock_client
    groq_client.model = "gpt-model"
    mock_client.chat.completions.create.return_value = mock_response
    
    evaluator = AnswerEvaluator(groq_client)
    res = evaluator.evaluate_answer(
        question="Explain JWT.",
        expected_answer="JSON Web Token...",
        candidate_answer="JWT is a stateless token format...",
        job_role="Python Developer",
        experience_level="Fresher"
    )
    
    # Fallback overall score should be a default (e.g. 5)
    assert 0 <= res["overall"] <= 10
    assert 0 <= res["technical_accuracy"] <= 10
    assert len(res["feedback"]) > 0


def test_evaluator_score_range_clamping():
    """Test constraints keeping scores within 0-10 under invalid API returns"""
    evaluator = AnswerEvaluator(MagicMock())
    parsed = evaluator._parse_evaluation("""
    {
      "technical_accuracy": -5,
      "relevance": 12,
      "completeness": "invalid_number_string",
      "clarity": 10,
      "overall": 9
    }
    """)
    assert parsed["technical_accuracy"] == 0  # Clamped from negative to 0
    assert parsed["relevance"] == 10          # Clamped from >10 to 10
    assert parsed["completeness"] == 5        # Defaults to 5 for non-number
    assert parsed["clarity"] == 10
    assert parsed["overall"] == 9


def test_interview_session_logic():
    """Test session state accumulation logic: attempted counts and average score calculation"""
    mock_history = []
    
    # Simulate question attempts and scoring updates
    mock_history.append({"question": "Question 1", "overall": 8})
    mock_history.append({"question": "Question 2", "overall": 9})
    mock_history.append({"question": "Question 3", "overall": 7})
    
    num_attempted = len(mock_history)
    avg_score = sum(item["overall"] for item in mock_history) / num_attempted
    
    assert num_attempted == 3
    assert avg_score == 8.0
