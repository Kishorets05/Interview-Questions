"""
Main Streamlit Application Entry Point
"""
import streamlit as st
import sys
import os
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.question_generator import QuestionGenerator
from config.config import (
    get_api_key,
    MODEL_NAME,
    EXPERIENCE_LEVELS,
    DIFFICULTY_LEVELS,
    TOPIC_FOCUS_OPTIONS,
    DEFAULT_NUM_QUESTIONS
)


def initialize_session_state():
    """Initialize session state variables"""
    if "questions_generated" not in st.session_state:
        st.session_state.questions_generated = False
    if "generated_data" not in st.session_state:
        st.session_state.generated_data = None
    if "question_chats" not in st.session_state:
        st.session_state.question_chats = {}  # Store chat history per question
    if "interview_mode" not in st.session_state:
        st.session_state.interview_mode = "Question Generator"
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "interview_completed" not in st.session_state:
        st.session_state.interview_completed = False
    if "current_question_idx" not in st.session_state:
        st.session_state.current_question_idx = 0
    if "mock_questions" not in st.session_state:
        st.session_state.mock_questions = []
    if "mock_history" not in st.session_state:
        st.session_state.mock_history = []
    if "current_evaluation" not in st.session_state:
        st.session_state.current_evaluation = None


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Interview Question Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    # Header Section with colorful design using Streamlit components
    col_header1, col_header2, col_header3 = st.columns([1, 3, 1])
    with col_header2:
        st.markdown("# 🚀 Interview Question Generator")
        st.markdown("### Generate personalized interview questions tailored to your needs")
        st.markdown(f"**Powered by {MODEL_NAME} via Groq API**")
    
    st.divider()
    
    # Info banner with visible text
    st.info("💡 **Tip:** Fill in the configuration settings on the left sidebar to generate customized interview questions!")
    
    # Sidebar for inputs with colorful sections
    with st.sidebar:
        st.markdown("## ⚙️ Configuration Settings")
        st.markdown("---")
        
        # Check API key status
        current_api_key = get_api_key()
        if not current_api_key:
            st.warning("⚠️ **Groq API Key Missing**\nConfigure `GROQ_API_KEY` in environment variables or Streamlit secrets.")
        
        st.markdown("### 🛠️ App Mode")
        mode = st.selectbox(
            "Select Mode",
            options=["Question Generator", "Mock Interview"],
            help="Choose between generating general/personalized questions, or starting an interactive mock interview."
        )
        st.session_state.interview_mode = mode

        st.divider()

        # Resume Upload
        st.markdown("### 📄 Resume Parsing")
        resume_file = st.file_uploader("Upload Resume (Optional PDF)", type=["pdf"])
        resume_text = None
        if resume_file:
            from backend.resume_parser import ResumeParser
            try:
                resume_text = ResumeParser.extract_text(resume_file)
                st.success("✅ Resume parsed successfully!")
            except Exception as e:
                st.error(f"❌ Parse error: {str(e)}")
        
        st.divider()
        
        # Job Role Input in a container
        with st.container():
            st.markdown("### 📝 Job Details")
            job_role = st.text_input(
                "Job Role *",
                placeholder="e.g., Java Developer, Python Developer",
                help="Enter the job role you're preparing for",
                label_visibility="visible"
            )
            
            # Experience Level
            experience_level = st.selectbox(
                "Experience Level *",
                options=EXPERIENCE_LEVELS,
                help="Select your experience level",
                label_visibility="visible"
            )
        
        st.divider()
        
        # Difficulty and Topic in a container
        with st.container():
            st.markdown("### 🎯 Question Settings")
            # Difficulty Level
            difficulty = st.selectbox(
                "Difficulty Level *",
                options=DIFFICULTY_LEVELS,
                index=1,  # Default to Medium
                help="Select the difficulty level of questions",
                label_visibility="visible"
            )
            
            # Topic Focus (Optional)
            topic_focus = st.selectbox(
                "Topic Focus (Optional)",
                options=["None"] + TOPIC_FOCUS_OPTIONS,
                help="Select a specific topic to focus on (optional)",
                label_visibility="visible"
            )
            
            if topic_focus == "None":
                topic_focus = None
            
            # Number of Questions (Optional)
            num_questions_input = st.text_input(
                "Number of Questions (Optional)",
                placeholder="Leave empty for default (5)",
                help="Enter number of questions to generate, or leave empty for default",
                label_visibility="visible"
            )
            
            num_questions = None
            if num_questions_input.strip():
                try:
                    num_questions = int(num_questions_input.strip())
                    if num_questions < 1:
                        st.warning("⚠️ Number must be at least 1")
                        num_questions = None
                except ValueError:
                    st.warning("⚠️ Please enter a valid number")
                    num_questions = None
        
        st.divider()
        
        # Generate Button with emphasis
        button_label = "🚀 Start Mock Interview" if st.session_state.interview_mode == "Mock Interview" else "🚀 Generate Questions"
        generate_button = st.button(
            button_label,
            type="primary",
            use_container_width=True
        )
        
        st.divider()
        
        # About section
        with st.expander("ℹ️ About This Tool", expanded=False):
            st.markdown(
                """
                **Features:**
                - ✅ Clear, structured answers
                - ✅ Difficulty-appropriate explanations
                - ✅ Tips to answer effectively
                - ✅ Common mistakes to avoid
                - ✅ Follow-up questions
                - ✅ Interactive chat for each question
                """
            )
    
    # Main content area
    if generate_button:
        # Validate inputs
        if not job_role.strip():
            st.error("❌ Please enter a job role!")
            return
        
        # Retrieve current API key
        api_key = get_api_key()
        if not api_key:
            st.error("❌ **Groq API Key is missing!** Please set the `GROQ_API_KEY` environment variable, add it to Streamlit Secrets, or place it in a `Groq api key.txt` file.")
            return

        if st.session_state.interview_mode == "Mock Interview":
            # Reset mock interview states
            st.session_state.mock_questions = []
            st.session_state.mock_history = []
            st.session_state.current_question_idx = 0
            st.session_state.interview_started = True
            st.session_state.interview_completed = False
            st.session_state.current_evaluation = None
            
            with st.spinner("🤖 Preparing your mock interview questions..."):
                try:
                    generator = QuestionGenerator(api_key)
                    result = generator.generate(
                        job_role=job_role,
                        experience_level=experience_level,
                        difficulty=difficulty,
                        topic_focus=topic_focus,
                        num_questions=num_questions,
                        resume_text=resume_text
                    )
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                        st.session_state.interview_started = False
                        return
                    
                    st.session_state.mock_questions = result.get("questions", [])
                    if not st.session_state.mock_questions:
                        st.error("❌ No questions were generated. Please try again.")
                        st.session_state.interview_started = False
                        return
                except Exception as e:
                    st.error(f"❌ Failed to start mock interview: {str(e)}")
                    st.session_state.interview_started = False
                    return
        else:
            # Clear previous chat history when generating new questions
            st.session_state.question_chats = {}
            st.session_state.questions_generated = False
            st.session_state.generated_data = None
            
            # Show loading
            with st.spinner("🤖 Generating interview questions... This may take a few seconds."):
                try:
                    # Initialize generator
                    generator = QuestionGenerator(api_key)
                    
                    # Generate questions
                    result = generator.generate(
                        job_role=job_role,
                        experience_level=experience_level,
                        difficulty=difficulty,
                        topic_focus=topic_focus,
                        num_questions=num_questions,
                        resume_text=resume_text
                    )
                    
                    # Check for errors
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                        return
                    
                    # Store in session state
                    st.session_state.generated_data = result
                    st.session_state.questions_generated = True
                    # Initialize chat history for each question
                    for idx in range(len(result.get("questions", []))):
                        st.session_state.question_chats[f"q_{idx}"] = []
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    return
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                return
    
    # Display results
    if st.session_state.interview_mode == "Mock Interview" and st.session_state.interview_started:
        display_mock_interview(job_role, experience_level)
    elif st.session_state.interview_mode == "Question Generator" and st.session_state.questions_generated and st.session_state.generated_data:
        display_results(st.session_state.generated_data)


def display_mock_interview(job_role: str, experience_level: str):
    """Render Mock Interview UI"""
    questions = st.session_state.mock_questions
    idx = st.session_state.current_question_idx
    
    if not questions:
        st.warning("No mock interview questions loaded. Please configure and start again.")
        return
        
    st.markdown("## 🎙️ Mock Interview Session")
    st.divider()
    
    # Check if completed
    if st.session_state.interview_completed or idx >= len(questions):
        st.session_state.interview_completed = True
        render_interview_summary(job_role, experience_level)
        return
        
    # Display Progress
    st.markdown(f"### Question {idx + 1} of {len(questions)}")
    progress_val = (idx) / len(questions)
    st.progress(progress_val)
    
    current_q = questions[idx]
    
    # Display Question
    st.info(f"**❓ {current_q['question']}**")
    
    # User Input
    answer_input = st.text_area(
        "Type your answer below:",
        height=150,
        placeholder="Enter your technical response here...",
        key=f"mock_answer_input_{idx}"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        submit_btn = st.button("Submit Answer", type="primary", use_container_width=True)
        
    if submit_btn:
        if not answer_input.strip():
            st.warning("⚠️ Please provide an answer before submitting.")
            return
            
        with st.spinner("🤖 Analyzing your answer..."):
            try:
                from backend.evaluator import AnswerEvaluator
                api_key = get_api_key()
                generator = QuestionGenerator(api_key)
                evaluator = AnswerEvaluator(generator.groq_client)
                
                eval_res = evaluator.evaluate_answer(
                    question=current_q["question"],
                    expected_answer=current_q["answer"],
                    candidate_answer=answer_input,
                    job_role=job_role,
                    experience_level=experience_level
                )
                
                # Save to history
                st.session_state.mock_history.append({
                    "question": current_q["question"],
                    "expected_answer": current_q["answer"],
                    "candidate_answer": answer_input,
                    "technical_accuracy": eval_res["technical_accuracy"],
                    "relevance": eval_res["relevance"],
                    "completeness": eval_res["completeness"],
                    "clarity": eval_res["clarity"],
                    "overall": eval_res["overall"],
                    "feedback": eval_res["feedback"]
                })
                
                st.session_state.current_evaluation = eval_res
                
            except Exception as e:
                st.error(f"❌ Answer evaluation failed: {str(e)}")
                
    # Display evaluation if exists for the current question
    if st.session_state.current_evaluation:
        eval_res = st.session_state.current_evaluation
        st.markdown("#### 📊 Evaluation Results")
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Overall", f"{eval_res['overall']}/10")
        c2.metric("Accuracy", f"{eval_res['technical_accuracy']}/10")
        c3.metric("Relevance", f"{eval_res['relevance']}/10")
        c4.metric("Completeness", f"{eval_res['completeness']}/10")
        c5.metric("Clarity", f"{eval_res['clarity']}/10")
        
        st.markdown(f"**💬 Feedback:**\n{eval_res['feedback']}")
        
        # Next / Finish Button
        is_last = (idx == len(questions) - 1)
        next_label = "Finish Interview" if is_last else "Next Question ➡️"
        
        next_btn = st.button(next_label, type="secondary")
        if next_btn:
            st.session_state.current_evaluation = None
            if is_last:
                st.session_state.interview_completed = True
            else:
                st.session_state.current_question_idx += 1
            st.rerun()


def render_interview_summary(job_role: str, experience_level: str):
    """Render the summary view of mock interview"""
    st.success("🎉 **Interview Session Completed!**")
    
    history = st.session_state.mock_history
    if not history:
        st.info("No answers submitted during this session.")
        st.button("Start New Session", on_click=reset_mock_interview)
        return
        
    num_attempted = len(history)
    avg_score = sum(item["overall"] for item in history) / num_attempted
    
    col1, col2 = st.columns(2)
    col1.metric("Questions Attempted", f"{num_attempted}")
    col2.metric("Average Score", f"{avg_score:.1f}/10")
    
    # Request summary from AI
    with st.spinner("🤖 Summarizing your overall strengths and improvements..."):
        try:
            from backend.evaluator import AnswerEvaluator
            api_key = get_api_key()
            generator = QuestionGenerator(api_key)
            evaluator = AnswerEvaluator(generator.groq_client)
            summary = evaluator.generate_interview_summary(history)
        except Exception:
            summary = {
                "strengths": ["Completed the interview session successfully."],
                "improvements": ["Review questions and practice concept-based responses."]
            }
            
    st.markdown("### 🏆 Performance Summary")
    st.divider()
    
    col_str, col_imp = st.columns(2)
    with col_str:
        st.markdown("#### 💪 Key Strengths")
        for s in summary.get("strengths", []):
            st.markdown(f"• {s}")
            
    with col_imp:
        st.markdown("#### 📈 Areas to Improve")
        for i in summary.get("improvements", []):
            st.markdown(f"• {i}")
            
    st.markdown("---")
    st.markdown("### 📖 Detailed Review")
    
    for idx, item in enumerate(history, 1):
        with st.expander(f"Question {idx}: {item['question'][:60]}... (Score: {item['overall']}/10)"):
            st.markdown(f"**Question:** {item['question']}")
            st.markdown(f"**Ideal Answer:** {item['expected_answer']}")
            st.markdown(f"**Your Answer:** {item['candidate_answer']}")
            st.markdown(f"**Feedback:** {item['feedback']}")
            st.markdown(f"**Scores:** Accuracy: {item['technical_accuracy']}/10, Relevance: {item['relevance']}/10, Completeness: {item['completeness']}/10, Clarity: {item['clarity']}/10")
            
    st.button("Start New Session", on_click=reset_mock_interview)


def reset_mock_interview():
    st.session_state.interview_started = False
    st.session_state.interview_completed = False
    st.session_state.current_question_idx = 0
    st.session_state.mock_questions = []
    st.session_state.mock_history = []
    st.session_state.current_evaluation = None


def display_results(data: dict):
    """Display the generated questions and answers"""
    questions = data.get("questions", [])
    metadata = data.get("metadata", {})
    
    if not questions:
        st.warning("No questions were generated. Please try again.")
        return
    
    # Display metadata using Streamlit metrics with uniform layout
    st.markdown("## 📊 Generation Summary")
    st.divider()
    
    # Use columns with slightly wider first column for job role
    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
    
    with col1:
        job_role = metadata.get("job_role", "N/A")
        st.markdown("**💼 Job Role**")
        st.markdown(f'<p style="font-size: 1.1rem; font-weight: 600; margin-top: 0.5rem; word-wrap: break-word;">{job_role}</p>', unsafe_allow_html=True)
    
    with col2:
        experience = metadata.get("experience_level", "N/A")
        st.markdown("**👤 Experience**")
        st.markdown(f'<p style="font-size: 1.1rem; font-weight: 600; margin-top: 0.5rem;">{experience}</p>', unsafe_allow_html=True)
    
    with col3:
        difficulty = metadata.get("difficulty", "N/A")
        st.markdown("**📈 Difficulty**")
        st.markdown(f'<p style="font-size: 1.1rem; font-weight: 600; margin-top: 0.5rem;">{difficulty}</p>', unsafe_allow_html=True)
    
    with col4:
        num_questions = len(questions)
        st.markdown("**❓ Questions**")
        st.markdown(f'<p style="font-size: 1.1rem; font-weight: 600; margin-top: 0.5rem;">{num_questions}</p>', unsafe_allow_html=True)
    
    if metadata.get("topic_focus"):
        st.success(f"📌 **Topic Focus:** {metadata['topic_focus']}")
    
    st.divider()
    st.markdown("## 📝 Generated Questions")
    st.markdown("")
    
    # Display each question in a structured, ordered format
    for idx, q in enumerate(questions, 1):
        # Question container using Streamlit components
        with st.container():
            st.markdown(f"## Question {idx}")
            st.divider()
            
            # Question Text - Clean and display
            question_text = str(q.get('question', 'N/A')).strip()
            # Remove any JSON artifacts that might be in the question
            if question_text.startswith('"') and question_text.endswith('"'):
                question_text = question_text[1:-1]
            # Remove escape characters
            question_text = question_text.replace('\\"', '"').replace('\\n', '\n')
            
            st.markdown(f"**❓ {question_text}**")
            st.markdown("")  # Spacing
            
            # Answer Section
            answer_text = str(q.get('answer', 'No answer provided')).strip()
            # Clean answer text
            if answer_text.startswith('"') and answer_text.endswith('"'):
                answer_text = answer_text[1:-1]
            answer_text = answer_text.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            
            # Ensure bullet points are properly formatted with line breaks
            # Replace bullet points followed by text to ensure proper line breaks
            answer_text = re.sub(r'•\s*', '\n• ', answer_text)
            # Ensure each bullet point starts on a new line
            answer_text = re.sub(r'([^\n])(•\s)', r'\1\n\2', answer_text)
            # Clean up multiple consecutive newlines
            answer_text = re.sub(r'\n{3,}', '\n\n', answer_text)
            answer_text = answer_text.strip()
            
            # Display answer (even if it says "No answer provided" or "Answer not available")
            st.markdown("**📖 Answer:**")
            if answer_text and answer_text not in ["No answer provided", "Answer not available.", "Answer is being generated. Please try regenerating the questions."]:
                st.markdown(answer_text)
            else:
                st.warning("Answer is not available. Please try regenerating the questions or check your API connection.")
            st.markdown("")  # Spacing
            
            # Explanation Section
            explanation = str(q.get('explanation', '')).strip()
            if explanation and explanation != "Response parsing encountered an issue.":
                if explanation.startswith('"') and explanation.endswith('"'):
                    explanation = explanation[1:-1]
                explanation = explanation.replace('\\"', '"').replace('\\n', '\n')
                
                st.markdown("**💡 Explanation:**")
                st.markdown(explanation)
                st.markdown("")  # Spacing
            
            # Tips Section
            tips = q.get('tips', [])
            if tips and isinstance(tips, list) and len(tips) > 0:
                # Filter out empty tips and clean them
                clean_tips = [str(tip).strip() for tip in tips if str(tip).strip() and not str(tip).strip().startswith('"tips"')]
                if clean_tips:
                    st.markdown("**✅ Tips to Answer:**")
                    for tip in clean_tips:
                        # Clean tip text
                        tip_clean = tip.replace('\\"', '"').replace('\\n', '\n')
                        if tip_clean.startswith('"') and tip_clean.endswith('"'):
                            tip_clean = tip_clean[1:-1]
                        st.markdown(f"• {tip_clean}")
                    st.markdown("")  # Spacing
            
            # Common Mistakes Section
            mistakes = q.get('common_mistakes', [])
            if mistakes and isinstance(mistakes, list) and len(mistakes) > 0:
                clean_mistakes = [str(mistake).strip() for mistake in mistakes if str(mistake).strip() and not str(mistake).strip().startswith('"common_mistakes"')]
                if clean_mistakes:
                    st.markdown("**⚠️ Common Mistakes:**")
                    for mistake in clean_mistakes:
                        mistake_clean = mistake.replace('\\"', '"').replace('\\n', '\n')
                        if mistake_clean.startswith('"') and mistake_clean.endswith('"'):
                            mistake_clean = mistake_clean[1:-1]
                        st.markdown(f"• {mistake_clean}")
                    st.markdown("")  # Spacing
            
            # Follow-up Questions Section
            follow_ups = q.get('follow_up_questions', [])
            if follow_ups and isinstance(follow_ups, list) and len(follow_ups) > 0:
                clean_follow_ups = [str(fu).strip() for fu in follow_ups if str(fu).strip() and not str(fu).strip().startswith('"follow_up_questions"')]
                if clean_follow_ups:
                    st.markdown("**🔄 Follow-up Questions:**")
                    for follow_up in clean_follow_ups:
                        fu_clean = follow_up.replace('\\"', '"').replace('\\n', '\n')
                        if fu_clean.startswith('"') and fu_clean.endswith('"'):
                            fu_clean = fu_clean[1:-1]
                        st.markdown(f"• {fu_clean}")
                    st.markdown("")  # Spacing
            
            # Chat Interface for Follow-up Queries
            st.markdown("---")
            st.markdown("#### 💬 Ask Questions About This Topic")
            st.markdown("*You can ask multiple questions - each question will be answered based on the context of this interview question.*")
            
            # Initialize chat history for this question if not exists
            chat_key = f"q_{idx-1}"
            if chat_key not in st.session_state.question_chats:
                st.session_state.question_chats[chat_key] = []
            
            # Get chat history for this question
            chat_history = st.session_state.question_chats[chat_key]
            
            # Display all previous chat history
            if chat_history:
                for chat_item in chat_history:
                    with st.chat_message("user"):
                        st.write(chat_item["query"])
                    with st.chat_message("assistant"):
                        st.write(chat_item["response"])
            
            # Chat input - allows unlimited questions
            user_query = st.chat_input(
                f"Ask a question about Question {idx}...",
                key=f"chat_input_{idx}"
            )
            
            # Process new query if submitted
            if user_query:
                # Add user query to history immediately (will show after rerun)
                st.session_state.question_chats[chat_key].append({
                    "query": user_query,
                    "response": ""  # Will be filled below
                })
                
                # Display user query
                with st.chat_message("user"):
                    st.write(user_query)
                
                # Generate response
                response = ""
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            # Retrieve current API key
                            api_key = get_api_key()
                            if not api_key:
                                st.error("❌ **Groq API Key is missing!**")
                                return
                                
                            generator = QuestionGenerator(api_key)
                            metadata = data.get("metadata", {})
                            
                            response = generator.answer_followup(
                                question_text=question_text,
                                question_answer=answer_text if answer_text != "No answer provided" else "",
                                user_query=user_query,
                                job_role=metadata.get("job_role", ""),
                                experience_level=metadata.get("experience_level", "")
                            )
                            
                            st.write(response)
                            
                        except Exception as e:
                            error_msg = f"Error generating response: {str(e)}"
                            st.error(error_msg)
                            response = error_msg
                
                # Update the last item in chat history with the response
                if st.session_state.question_chats[chat_key]:
                    st.session_state.question_chats[chat_key][-1]["response"] = response
            
            st.markdown("---")


if __name__ == "__main__":
    main()

