"""
Question Generator Service
"""
from typing import Dict, Optional
from backend.groq_client import GroqClient


class QuestionGenerator:
    """Service for generating interview questions"""
    
    def __init__(self, api_key: str):
        """
        Initialize question generator
        
        Args:
            api_key: Groq API key
        """
        self.groq_client = GroqClient(api_key)
    
    def generate(
        self,
        job_role: str,
        experience_level: str,
        difficulty: str,
        topic_focus: Optional[str] = None,
        num_questions: Optional[int] = None
    ) -> Dict:
        """
        Generate interview questions
        
        Args:
            job_role: Job role
            experience_level: Experience level
            difficulty: Difficulty level
            topic_focus: Optional topic focus
            num_questions: Number of questions
            
        Returns:
            Dictionary with questions and metadata
        """
        try:
            result = self.groq_client.generate_interview_questions(
                job_role=job_role,
                experience_level=experience_level,
                difficulty=difficulty,
                topic_focus=topic_focus,
                num_questions=num_questions
            )
            
            # Add metadata
            result["metadata"] = {
                "job_role": job_role,
                "experience_level": experience_level,
                "difficulty": difficulty,
                "topic_focus": topic_focus,
                "num_questions": len(result.get("questions", []))
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "questions": [],
                "metadata": {}
            }
    
    def answer_followup(
        self,
        question_text: str,
        question_answer: str,
        user_query: str,
        job_role: str,
        experience_level: str
    ) -> str:
        """
        Answer a follow-up query related to a specific question
        
        Args:
            question_text: Original question
            question_answer: Original answer
            user_query: User's follow-up query
            job_role: Job role context
            experience_level: Experience level context
            
        Returns:
            Response to the query
        """
        return self.groq_client.answer_followup_query(
            question_text, question_answer, user_query, job_role, experience_level
        )

