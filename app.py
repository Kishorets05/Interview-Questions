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
    GROQ_API_KEY,
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
        st.markdown("**Powered by LLaMA-3-70B-Instruct via Groq API**")
    
    st.divider()
    
    # Info banner with visible text
    st.info("💡 **Tip:** Fill in the configuration settings on the left sidebar to generate customized interview questions!")
    
    # Sidebar for inputs with colorful sections
    with st.sidebar:
        st.markdown("## ⚙️ Configuration Settings")
        st.markdown("---")
        
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
        generate_button = st.button(
            "🚀 Generate Questions",
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
        
        # Clear previous chat history when generating new questions
        st.session_state.question_chats = {}
        
        # Show loading
        with st.spinner("🤖 Generating interview questions... This may take a few seconds."):
            try:
                # Initialize generator
                generator = QuestionGenerator(GROQ_API_KEY)
                
                # Generate questions
                result = generator.generate(
                    job_role=job_role,
                    experience_level=experience_level,
                    difficulty=difficulty,
                    topic_focus=topic_focus,
                    num_questions=num_questions
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
    
    # Display results
    if st.session_state.questions_generated and st.session_state.generated_data:
        display_results(st.session_state.generated_data)


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
                            generator = QuestionGenerator(GROQ_API_KEY)
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

