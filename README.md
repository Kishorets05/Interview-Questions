# Interview Question Generator

A Streamlit-based web application that generates personalized interview questions using Groq API and LLaMA-3-70B-Instruct model.

🌐 **Live Demo:** [https://interview-questions-cjdkvgk3cudkfaxrwunkvt.streamlit.app/](https://interview-questions-cjdkvgk3cudkfaxrwunkvt.streamlit.app/)

## Features

- **Customizable Inputs:**
  - Job role (e.g., Java Developer, Python Developer)
  - Experience level (Fresher, 1 Year, 2 Years, etc.)
  - Difficulty level (Easy, Medium, Hard)
  - Optional topic focus (OOP, DBMS, DSA, CN, etc.)
  - Adjustable number of questions (3-10)

- **Comprehensive Outputs:**
  - Interview questions tailored to your inputs
  - Clear, structured answers
  - Difficulty-appropriate explanations
  - Tips to answer effectively
  - Common mistakes to avoid
  - Follow-up questions for deeper understanding

## Project Structure

```
Interview Questions/
├── app.py                 # Main Streamlit application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── backend/
│   ├── groq_client.py    # Groq API client
│   └── question_generator.py  # Question generation service
└── config/
    └── config.py         # Configuration settings
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "Interview Questions"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Use the Live Demo
- Visit the live application: [https://interview-questions-cjdkvgk3cudkfaxrwunkvt.streamlit.app/](https://interview-questions-cjdkvgk3cudkfaxrwunkvt.streamlit.app/)
- No installation required!

### Option 2: Run Locally

1. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser:**
   - The app will automatically open in your default browser
   - Or navigate to `http://localhost:8501`

3. **Fill in the form:**
   - Enter your job role
   - Select your experience level
   - Choose difficulty level
   - Optionally select a topic focus
   - Adjust the number of questions

4. **Generate questions:**
   - Click "Generate Questions" button
   - Wait for the AI to generate questions (may take a few seconds)

5. **View results:**
   - Questions will be displayed with expandable sections for:
     - Answers
     - Explanations
     - Tips
     - Common mistakes
     - Follow-up questions

## Configuration

The API key is configured in `config/config.py`. You can also set it as an environment variable:

```bash
export GROQ_API_KEY="your_api_key_here"
```

## Technologies Used

- **Streamlit**: Web framework for the UI
- **Groq API**: For AI-powered question generation
- **LLaMA-3-70B-Instruct**: Large language model for generating questions

## Notes

- The application uses the Groq API which requires an internet connection
- Response times may vary based on API load
- Generated questions are AI-powered and should be reviewed for accuracy

## Troubleshooting

If you encounter errors:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check your internet connection
3. Verify the API key is correct
4. Check the console for detailed error messages




