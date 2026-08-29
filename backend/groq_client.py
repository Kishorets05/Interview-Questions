"""
Groq API Client for generating interview questions
"""
import os
import re
from groq import Groq, APIError, APIConnectionError, RateLimitError, AuthenticationError, NotFoundError
from typing import Dict, List, Optional
from config.config import MODEL_NAME


class GroqClient:
    """Client for interacting with Groq API using LLaMA-3-70B-Instruct"""
    
    def __init__(self, api_key: str):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key
        """
        self.client = Groq(api_key=api_key)
        self.model = MODEL_NAME
    
    def generate_interview_questions(
        self,
        job_role: str,
        experience_level: str,
        difficulty: str,
        topic_focus: Optional[str] = None,
        num_questions: Optional[int] = None
    ) -> Dict:
        """
        Generate interview questions based on user inputs
        
        Args:
            job_role: Job role (e.g., Java Developer)
            experience_level: Experience level (e.g., Fresher, 2 Years)
            difficulty: Difficulty level (Easy, Medium, Hard)
            topic_focus: Optional topic focus (OOP, DBMS, DSA, CN, etc.)
            num_questions: Number of questions to generate
            
        Returns:
            Dictionary containing questions and answers
        """
        # Build the prompt
        if num_questions is None:
            num_questions = 5  # Default if not specified
        prompt = self._build_prompt(
            job_role, experience_level, difficulty, topic_focus, num_questions
        )
        
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical interviewer. Generate interview questions with detailed answers, tips, common mistakes, and follow-up questions in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Parse the response (assuming structured format)
            return self._parse_response(content)
            
        except AuthenticationError:
            raise Exception("Invalid Groq API key. Please check your configuration and verify that your API key is correct and active.")
        except NotFoundError:
            raise Exception(f"The model '{self.model}' is not available or you do not have access to it. Please check your account/model access.")
        except RateLimitError:
            raise Exception("Groq API rate limit exceeded. Please wait a moment before trying again.")
        except APIConnectionError:
            raise Exception("Failed to connect to the Groq API. Please verify your internet connection.")
        except APIError as e:
            raise Exception(f"Groq API error: {e.message}")
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")
    
    def _build_prompt(
        self,
        job_role: str,
        experience_level: str,
        difficulty: str,
        topic_focus: Optional[str],
        num_questions: int
    ) -> str:
        """Build the prompt for the API"""
        prompt = f"""Generate {num_questions} interview questions for a {job_role} position.

Experience Level: {experience_level}
Difficulty: {difficulty}
"""
        if topic_focus:
            prompt += f"Topic: {topic_focus}\n"
        
        prompt += """
Return ONLY valid JSON with NO markdown or code blocks:
{"questions": [{"question": "...", "answer": "...", "explanation": "...", "tips": ["..."], "common_mistakes": ["..."], "follow_up_questions": ["..."]}]}

Requirements:
- Each answer must be 2-3 sentences minimum
- Include practical examples where relevant
- Tips should be actionable (2-3 tips)
- Common mistakes (1-2 realistic examples)
- Follow-up questions (1-2 probing questions)
- Match complexity to the difficulty level
"""
        return prompt
    
    def _parse_response(self, content: str) -> Dict:
        """Parse the API response"""
        import json
        import re
        
        # Clean the content
        original_content = content
        content = content.strip()
        
        # Try multiple strategies to extract JSON
        
        # Strategy 1: Extract from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1).strip()
        
        # Strategy 2: Find JSON object by matching braces
        if not json_match:
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                # Try to find balanced braces
                brace_count = 0
                for i in range(start_idx, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i
                            break
                content = content[start_idx:end_idx + 1]
        
        # Try to parse JSON
        parsed = None
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            # Remove trailing commas
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            # Fix unescaped quotes in strings (basic attempt)
            # Replace newlines in strings with \n
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # Try one more time with more aggressive cleaning
                # Remove any text before first { and after last }
                start = content.find('{')
                end = content.rfind('}')
                if start != -1 and end != -1 and end > start:
                    try:
                        parsed = json.loads(content[start:end+1])
                    except json.JSONDecodeError:
                        pass
        
        # Validate parsed JSON
        if parsed and isinstance(parsed, dict):
            if "questions" in parsed and isinstance(parsed["questions"], list):
                # Clean and validate each question
                cleaned_questions = []
                for q in parsed["questions"]:
                    if isinstance(q, dict):
                        cleaned_q = {
                            "question": str(q.get("question", "")).strip(),
                            "answer": str(q.get("answer", "")).strip(),
                            "explanation": str(q.get("explanation", "")).strip(),
                            "tips": self._ensure_list(q.get("tips", [])),
                            "common_mistakes": self._ensure_list(q.get("common_mistakes", [])),
                            "follow_up_questions": self._ensure_list(q.get("follow_up_questions", []))
                        }
                        # Validate that question and answer are not empty
                        if cleaned_q["question"]:
                            # If answer is empty or just whitespace, try to get it from original
                            if not cleaned_q["answer"] or cleaned_q["answer"].strip() == "":
                                # Try to extract answer from original content if available
                                original_answer = q.get("answer", "")
                                if original_answer and str(original_answer).strip():
                                    cleaned_q["answer"] = str(original_answer).strip()
                                else:
                                    cleaned_q["answer"] = "Answer is being generated. Please try regenerating the questions."
                            cleaned_questions.append(cleaned_q)
                
                if cleaned_questions:
                    return {"questions": cleaned_questions}
        
        # If parsing failed, try to extract questions from text
        return self._extract_questions_from_text(original_content)
    
    def _ensure_list(self, value):
        """Ensure value is a list of strings"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        elif isinstance(value, str):
            # Try to parse as JSON array
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except:
                pass
            # Split by common delimiters
            if value.strip():
                return [item.strip() for item in re.split(r'[,\n]', value) if item.strip()]
        return []
    
    def _extract_questions_from_text(self, text: str) -> Dict:
        """Extract questions from unstructured text as fallback"""
        import re
        questions = []
        
        # Try to find question patterns - improved to handle multi-line JSON
        # Pattern 1: "question": "..." followed by other fields
        # Use a more flexible pattern that can handle escaped quotes and newlines
        question_pattern = r'"question"\s*:\s*"((?:[^"\\]|\\.)+)"'
        matches = list(re.finditer(question_pattern, text, re.IGNORECASE | re.DOTALL))
        
        for match in matches:
            question_text = match.group(1).replace('\\"', '"').replace('\\n', '\n')
            # Try to extract answer - look for it after the question
            start_pos = match.end()
            # Look for answer within next 2000 characters (to handle longer answers)
            end_pos = min(start_pos + 2000, len(text))
            snippet = text[start_pos:end_pos]
            
            # Improved answer pattern - handles multi-line and escaped quotes
            answer_match = re.search(r'"answer"\s*:\s*"((?:[^"\\]|\\.)+)"', snippet, re.IGNORECASE | re.DOTALL)
            if answer_match:
                answer = answer_match.group(1).replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            else:
                # Try alternative pattern without quotes (in case JSON is malformed)
                answer_match2 = re.search(r'"answer"\s*:\s*([^,}]+)', snippet, re.IGNORECASE | re.DOTALL)
                if answer_match2:
                    answer = answer_match2.group(1).strip().strip('"').strip("'")
                else:
                    answer = "Answer not available."
            
            explanation_match = re.search(r'"explanation"\s*:\s*"((?:[^"\\]|\\.)+)"', snippet, re.IGNORECASE | re.DOTALL)
            if explanation_match:
                explanation = explanation_match.group(1).replace('\\"', '"').replace('\\n', '\n')
            else:
                explanation = ""
            
            questions.append({
                "question": question_text,
                "answer": answer,
                "explanation": explanation,
                "tips": [],
                "common_mistakes": [],
                "follow_up_questions": []
            })
        
        if questions:
            return {"questions": questions}
        
        # Last resort: return error message
        return {
            "questions": [{
                "question": "Unable to parse response. Please try again.",
                "answer": "The API response could not be parsed. This might be due to formatting issues. Please try generating questions again.",
                "explanation": "Parsing error occurred. The response format may not match the expected JSON structure.",
                "tips": ["Try generating again", "Check your internet connection", "Verify API key is valid"],
                "common_mistakes": [],
                "follow_up_questions": []
            }]
        }
    
    def answer_followup_query(
        self,
        question_text: str,
        question_answer: str,
        user_query: str,
        job_role: str,
        experience_level: str
    ) -> str:
        """
        Answer a follow-up query related to a specific interview question
        
        Args:
            question_text: The original interview question
            question_answer: The original answer to the question
            user_query: User's follow-up query
            job_role: Job role context
            experience_level: Experience level context
            
        Returns:
            Response to the user's query
        """
        prompt = f"""You are helping a candidate prepare for a {job_role} interview at {experience_level} level.

The candidate was asked this interview question:
"{question_text}"

The answer provided was:
"{question_answer}"

Now the candidate has a follow-up question:
"{user_query}"

Please provide a helpful, detailed answer to their follow-up question. Be specific and practical."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical interviewer and mentor helping candidates prepare for interviews. Provide clear, detailed, and helpful answers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except AuthenticationError:
            raise Exception("Invalid Groq API key. Please check your configuration.")
        except NotFoundError:
            raise Exception(f"The model '{self.model}' is not available.")
        except RateLimitError:
            raise Exception("Groq API rate limit exceeded. Please try again in a moment.")
        except APIConnectionError:
            raise Exception("Failed to connect to the Groq API. Please verify your internet connection.")
        except APIError as e:
            raise Exception(f"Groq API error: {e.message}")
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

