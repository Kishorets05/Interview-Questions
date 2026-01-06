"""
Configuration file
"""
import os

# Groq API Key (must be set as environment variable)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")


# Model Configuration
MODEL_NAME = "llama-3.1-8b-instant"

# Default Settings
DEFAULT_NUM_QUESTIONS = 5
DEFAULT_DIFFICULTY = "Medium"

# Available Options
EXPERIENCE_LEVELS = ["Fresher", "1 Year", "2 Years", "3 Years", "4 Years", "5+ Years"]
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
TOPIC_FOCUS_OPTIONS = [
    "OOP (Object-Oriented Programming)",
    "DBMS (Database Management System)",
    "DSA (Data Structures & Algorithms)",
    "CN (Computer Networks)",
    "OS (Operating Systems)",
    "SDLC (Software Development Life Cycle)",
    "System Design",
    "API Design",
    "Testing",
    "Security",
    "General"
]

