"""
Groq API Client for generating interview questions
"""
import os
import re
from groq import Groq
from typing import Dict, List, Optional


class GroqClient:
    """Client for interacting with Groq API using LLaMA-3-70B-Instruct"""
    
    def __init__(self, api_key: str):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key
        """
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
    
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
                        "content": "You are an expert technical interviewer and mentor. Generate comprehensive, well-structured interview questions with detailed answers, tips, common mistakes, and follow-up questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=8192
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Parse the response (assuming structured format)
            return self._parse_response(content)
            
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
        if num_questions:
            prompt = f"""Generate {num_questions} interview questions for a {job_role} position.

Experience Level: {experience_level}
Difficulty Level: {difficulty}
"""
        else:
            prompt = f"""Generate interview questions for a {job_role} position. Generate a comprehensive set of questions (typically 5-8 questions).

Experience Level: {experience_level}
Difficulty Level: {difficulty}
"""
        
        if topic_focus:
            prompt += f"Topic Focus: {topic_focus}\n"
        
        if num_questions:
            prompt += f"""
CRITICAL: You MUST respond with ONLY valid JSON. No markdown, no code blocks, no explanations, just pure JSON.

Generate exactly {num_questions} interview questions. Return ONLY this JSON structure:

{{"questions": [{{"question": "What is...?", "answer": "The answer is...", "explanation": "This tests...", "tips": ["Tip 1", "Tip 2"], "common_mistakes": ["Mistake 1"], "follow_up_questions": ["Follow-up 1"]}}]}}

IMPORTANT: Answers must be comprehensive, detailed, well-formatted, and match the question complexity:
- For simple/Easy questions: Provide 3-5 sentences minimum with clear explanations and basic examples
- For moderate questions: Provide 5-8 sentences with detailed explanations, examples, use cases, and practical applications
- For complex/Hard questions: Provide 8-12 sentences with comprehensive explanations, multiple examples, code snippets (if applicable), best practices, trade-offs, and real-world scenarios
- FORMAT ANSWERS FOR READABILITY:
  * Use bullet points (•) to break down key concepts, steps, or components
  * Start with a brief overview paragraph (2-3 sentences)
  * Then use bullet points for lists, steps, features, advantages, or components
  * Use paragraphs for detailed explanations
  * Mix paragraphs and bullet points for better readability
  * For step-by-step processes, use numbered or bulleted lists
  * For comparisons or multiple items, use bullet points
- Answers should be thorough enough to help someone understand the topic deeply
- Always include relevant examples and real-world applications
- For technical questions, include code examples or pseudocode when appropriate
- The answer length and depth must match the complexity and difficulty of the question

Example format (generate {num_questions} questions like this):
"""
        else:
            prompt += """
CRITICAL: You MUST respond with ONLY valid JSON. No markdown, no code blocks, no explanations, just pure JSON.

Generate a comprehensive set of interview questions (typically 5-8 questions). Return ONLY this JSON structure:

{"questions": [{"question": "What is...?", "answer": "The answer is...", "explanation": "This tests...", "tips": ["Tip 1", "Tip 2"], "common_mistakes": ["Mistake 1"], "follow_up_questions": ["Follow-up 1"]}]}

IMPORTANT: Answers must be comprehensive, well-formatted, and match question complexity:
- Simple/Easy: 3-5 sentences with clear explanations
- Moderate: 5-8 sentences with examples and use cases
- Complex/Hard: 8-12 sentences with detailed explanations, examples, code snippets, and best practices
- FORMAT FOR READABILITY: Use bullet points (•) for lists, steps, features, or components. Start with a brief overview, then use bullets for key points. Mix paragraphs and bullets for better readability.
- Always include examples and real-world applications
- Match answer depth to question complexity

Example format:
"""
        
        prompt += """
{
  "questions": [
    {
      "question": "Explain the concept of inheritance in object-oriented programming.",
      "answer": "Inheritance is a fundamental OOP concept that allows a class to inherit properties and methods from another class. The class that inherits is called the derived or child class, and the class being inherited from is called the base or parent class.\n\nKey aspects of inheritance:\n• Promotes code reusability by allowing child classes to use parent class functionality\n• Establishes an 'is-a' relationship between classes (e.g., Car is-a Vehicle)\n• Supports polymorphism, allowing child classes to override parent methods while maintaining the same interface\n• Enables hierarchical organization of code, making it easier to maintain and extend\n\nFor example, if we have a base class 'Vehicle' with properties like 'speed' and methods like 'start()', a child class 'Car' can inherit these and add its own specific properties like 'numberOfDoors'.\n\nHowever, it's important to use inheritance judiciously - composition is often preferred when there's no clear 'is-a' relationship to avoid tight coupling and maintain flexibility in the design.",
      "explanation": "This question tests the candidate's understanding of core OOP principles and their ability to explain technical concepts clearly.",
      "tips": ["Start with a clear definition", "Provide a practical example", "Mention benefits and use cases"],
      "common_mistakes": ["Confusing inheritance with composition", "Not explaining the relationship clearly"],
      "follow_up_questions": ["What is the difference between inheritance and composition?", "When would you prefer composition over inheritance?"]
    }
  ]
}

Requirements:
"""
        if num_questions:
            prompt += f"- Generate exactly {num_questions} questions\n"
        else:
            prompt += "- Generate a comprehensive set of questions (5-8 questions recommended)\n"
        
        prompt += f"""- Questions must match {experience_level} experience level
- Difficulty level: {difficulty}
- Each question must have all fields: question, answer, explanation, tips (array), common_mistakes (array), follow_up_questions (array)
- ANSWERS MUST BE COMPREHENSIVE, DETAILED, AND WELL-FORMATTED:
  * Simple/Easy questions: Provide 3-5 sentences minimum with clear explanations
  * Moderate questions: Provide 5-8 sentences with examples, use cases, and practical applications
  * Complex/Hard questions: Provide 8-12 sentences with detailed explanations, multiple examples, code snippets (if applicable), best practices, and real-world scenarios
  * FORMATTING FOR READABILITY:
    - Start with a brief overview paragraph (2-3 sentences)
    - Use bullet points (•) to break down key concepts, steps, features, advantages, or components
    - Mix paragraphs and bullet points for better readability
    - For step-by-step processes, use bulleted lists
    - For comparisons or multiple items, use bullet points
    - Avoid long, unbroken paragraphs - break them up with bullets where appropriate
  * Always include relevant examples and real-world applications
  * Match answer depth and length to the complexity of the question
  * For technical questions, include code examples or pseudocode when appropriate
- Explanations should be 2-3 sentences explaining why the question is asked and what it tests
- Tips should be practical and actionable (3-5 tips per question)
- Common mistakes should be specific and realistic (2-4 mistakes per question)
- Follow-up questions should be relevant and probing (2-3 follow-ups per question)
- Return ONLY the JSON, nothing else before or after
- Ensure all strings are properly escaped in JSON
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
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

