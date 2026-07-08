import os
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# GEMINI SETUP
# -----------------------------
API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# -----------------------------
# FUNCTIONS
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PdfReader(uploaded_file)

    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

def summarize_resume(resume_text):
    prompt = f"""
    Analyze this resume and provide:

    1. Candidate Summary
    2. Key Skills
    3. Strengths
    4. Suggested Interview Focus Areas

    Resume:
    {resume_text}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"ERROR: {str(e)}")
        return "Error"
 


def generate_questions(resume_text, role, difficulty):
    prompt = f"""
    Based on this resume:

    {resume_text}

    Generate 10 interview questions.

    Role: {role}
    Difficulty: {difficulty}

    Mix:
    - Technical
    - Behavioral
    - Problem Solving

    Return only numbered questions.
    """

    response = model.generate_content(prompt)
    return response.text


def evaluate_answer(question, answer):
    prompt = f"""
    You are an expert interviewer.

    Question:
    {question}

    Candidate Answer:
    {answer}

    Evaluate on:

    - Technical Accuracy (0-10)
    - Communication (0-10)
    - Confidence (0-10)

    Give detailed feedback.

    Return in this format:

    Technical Accuracy:
    Communication:
    Confidence:
    Overall Score:

    Feedback:
    """

    response = model.generate_content(prompt)
    return response.text


# -----------------------------
# SESSION STATE
# -----------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

# -----------------------------
# UI
# -----------------------------
st.title("🤖 AI Interview Assistant")

st.markdown(
    """
    Upload your resume and practice AI-generated interviews.
    """
)

uploaded_file = st.file_uploader(
    "Upload Resume (PDF/TXT)",
    type=["pdf", "txt"]
)

role = st.text_input(
    "Target Role",
    value="Software Engineer"
)

difficulty = st.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

# -----------------------------
# RESUME PROCESSING
# -----------------------------
if uploaded_file:

    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)

    else:
        resume_text = uploaded_file.read().decode("utf-8")

    st.success("Resume Loaded Successfully")

    with st.expander("Resume Preview"):
        st.text_area(
            "",
            resume_text[:5000],
            height=250
        )

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing Resume..."):
            summary = summarize_resume(resume_text)

        st.subheader("Resume Analysis")
        st.markdown(summary)

    if st.button("Generate Interview Questions"):
        with st.spinner("Generating Questions..."):
            questions_text = generate_questions(
                resume_text,
                role,
                difficulty
            )

        question_list = []

        for line in questions_text.split("\n"):
            line = line.strip()

            if len(line) > 5:
                question_list.append(line)

        st.session_state.questions = question_list
        st.session_state.current_question = 0

        st.success("Questions Generated")

# -----------------------------
# INTERVIEW SECTION
# -----------------------------
if st.session_state.questions:

    st.header("Interview Session")

    idx = st.session_state.current_question

    if idx < len(st.session_state.questions):

        question = st.session_state.questions[idx]

        st.subheader(
            f"Question {idx + 1} / {len(st.session_state.questions)}"
        )

        st.info(question)

        answer = st.text_area(
            "Your Answer",
            height=180,
            key=f"answer_{idx}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Evaluate Answer"):

                if answer.strip():

                    with st.spinner("Evaluating..."):
                        result = evaluate_answer(
                            question,
                            answer
                        )

                    st.markdown(result)

                else:
                    st.warning("Please enter an answer.")

        with col2:
            if st.button("Next Question"):

                st.session_state.current_question += 1
                st.rerun()

    else:
        st.success("Interview Completed 🎉")

        st.balloons()

        st.markdown(
            """
            ### Congratulations

            You have completed the AI interview session.
            """
        )
