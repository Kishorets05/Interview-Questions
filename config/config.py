"""
Configuration file
"""
import os

def get_api_key():
    # 1. Try to read from Streamlit secrets first if available
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    # 2. Try to read from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key

    # 3. Try to read from local file
    key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Groq api key.txt")
    if os.path.exists(key_file):
        try:
            with open(key_file, "r") as f:
                return f.read().strip()
        except Exception:
            pass

    return None

# Groq API Key - dynamically resolved
GROQ_API_KEY = get_api_key()


# Model Configuration
MODEL_NAME = "llama-3.3-70b-versatile"

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

