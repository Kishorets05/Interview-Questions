"""
Configuration file
"""
import os

# Groq API Key - read from environment variable or file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    # Try to read from file
    key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Groq api key.txt")
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            GROQ_API_KEY = f.read().strip()
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set and Groq api key.txt file not found")


# Model Configuration
MODEL_NAME = "llama-3.1-8b-instant"

# Default Settings
DEFAULT_NUM_QUESTIONS = 3
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

