# AI Interview Questions Generator

A Streamlit-based web application that generates personalized interview questions, handles mock interview practice, and grades candidate responses using the Groq API and Large Language Models (LLMs).

🌐 **Live Demo:** [https://interview-questions-cjdkvgk3cudkfaxrwunkvt.streamlit.app/](https://interview-questions-cjdkvgk3cudkfaxrwunkvt.streamlit.app/)

---

## Features

- **Customizable Inputs:**
  - Job role (e.g., Java Developer, Python Developer)
  - Experience level (Fresher, 1 Year, 2 Years, etc.)
  - Difficulty level (Easy, Medium, Hard)
  - Topic focus (OOP, DBMS, DSA, CN, etc.)
  - Adjustable number of questions (3-10)

- **Optional Resume Personalization:**
  - PDF Resume Upload: Extracts text dynamically to generate questions tailored specifically to the technologies, projects, and skills mentioned in your resume.

- **Dual Mode Support:**
  - **Question Generator Mode:** Generates a list of questions, complete with reference answers, comprehensive explanations, actionable tips, common mistakes to avoid, and follow-up questions.
  - **Mock Interview Mode:** Conducts an interactive interview session. Candidate submits answers, and the AI evaluates them in real-time, assigning numeric scores and qualitative feedback.

- **AI Answer Evaluation:**
  - Scores responses out of 10 across four key dimensions: **Technical Accuracy**, **Relevance**, **Completeness**, and **Clarity**, alongside an **Overall Score** and detailed feedback.

- **Session-Based Progress Tracking:**
  - Maintains state dynamically using `st.session_state` to track current questions, answer history, scores, and compile a finalRecruiter Performance Summary at the end of the interview.

---

## Technologies Used

- **Streamlit:** Frontend web framework for rendering UI components, handling file uploading, and tracking session states.
- **Groq API:** Ultra-high-speed inference API client for LLM interaction.
- **Large Language Models (LLMs):** Powered by `openai/gpt-oss-120b` for high-quality structured output generation.
- **pypdf:** Lightweight library used for extracting text from uploaded candidate PDF resumes.
- **Prompt Engineering:** Structuring system instructions, candidate context, and parameters to ensure strict structured output and consistent evaluation criteria.
- **pytest:** Automated test runner used for mocking API requests and validating core backend services.

---

## Project Structure

```text
Interview Questions/
│
├── app.py                     # Main Streamlit UI and session management
│
├── backend/
│   ├── groq_client.py         # Existing Groq API client with error handling
│   ├── question_generator.py  # Question generation service
│   ├── resume_parser.py       # PDF resume text extraction
│   └── evaluator.py           # Answer evaluation and recruting summary
│
├── config/
│   └── config.py              # Configuration and dynamic key resolution
│
├── tests/                     # Automated testing suite
│   ├── test_question_generator.py
│   ├── test_resume_parser.py
│   └── test_evaluator.py
│
├── requirements.txt           # Project dependencies
└── README.md                  # This file
```

---

## Installation & Setup

1. **Clone and navigate to the project directory:**
   ```bash
   cd "Interview Questions"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API Key:**
   Set the `GROQ_API_KEY` environment variable:
   - **Windows PowerShell:** `$env:GROQ_API_KEY="your_api_key_here"`
   - **Windows CMD:** `set GROQ_API_KEY=your_api_key_here`
   - **Linux/macOS Bash:** `export GROQ_API_KEY="your_api_key_here"`
   - **Alternative:** Create a file named `Groq api key.txt` in the project root containing your API key.

4. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

---

## Automated Testing

Automated tests are written with `pytest` and mock the LLM responses to avoid hitting API rate limits or consuming tokens.

### Run Tests

Execute the following command in the project root:
```bash
python -m pytest
```

### Areas Covered by Tests

1. **Resume Parser (`test_resume_parser.py`):**
   - Validates correct PDF text extraction.
   - Verifies appropriate exceptions for empty files, invalid PDFs, and missing inputs.

2. **Question Generator (`test_question_generator.py`):**
   - Verifies that job details, experience levels, difficulty, and selected topics are correctly formatted in prompt generation.
   - Confirms that resume context is appended only when provided.
   - Assures valid JSON is parsed correctly, while invalid JSON is recovered gracefully.

3. **Answer Evaluator (`test_evaluator.py`):**
   - Verifies score range clamping (ensuring overall scores remain strictly between `0` and `10`).
   - Confirms invalid LLM evaluation responses are handled safely with fallback grades.
   - Validates that empty candidate answers immediately receive `0` without making external API calls.
   - Validates session tracking math (calculating the correct question counts and average overall scores).

---

## Error Handling

The application implements granular exception handling for reliability:
- **AuthenticationError:** Warns the user of an invalid API key, with setup instructions.
- **NotFoundError:** Gracefully lists available models for the user's API key if a configured model is unavailable.
- **RateLimitError:** Notifies the user of rate limit caps and requests them to retry shortly.
- **Invalid PDF Format:** Informs the candidate of PDF extraction failures.
- **API Connection Error:** Alerts the user to check network connectivity.
- **JSON Parsing Recovery:** Performs regex extraction on malformed LLM outputs to recover questions, scores, and feedback cleanly without crashing.
