import os
import re
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------
# GEMINI SETUP
# ---------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# ---------------------------------
# SESSION STATE
# ---------------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "scores" not in st.session_state:
    st.session_state.scores = []

# ---------------------------------
# FUNCTIONS
# ---------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""

    pdf = PdfReader(uploaded_file)

    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def summarize_resume(resume_text):

    prompt = f"""
    Analyze the resume.

    Return:

    1. Candidate Summary
    2. Key Skills
    3. Strengths
    4. Weaknesses
    5. Suggested Career Roles

    Resume:
    {resume_text}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"


def generate_questions(resume_text, role, difficulty):

    prompt = f"""
    Resume:

    {resume_text}

    Generate 10 interview questions.

    Role: {role}

    Difficulty: {difficulty}

    Mix:
    - Technical
    - HR
    - Problem Solving
    - Project Based

    Return only numbered questions.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"


def evaluate_answer(question, answer):

    prompt = f"""
    You are an expert interviewer.

    Question:
    {question}

    Candidate Answer:
    {answer}

    Give score out of 10.

    Format EXACTLY:

    Technical Accuracy: X
    Communication: X
    Confidence: X

    Feedback:
    Your feedback

    Strength:
    Candidate strength

    Weakness:
    Candidate weakness
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------
# HEADER
# ---------------------------------
st.title("🤖 AI Interview Assistant")

st.markdown("""
### Features

✅ Resume Analysis

✅ AI Generated Questions

✅ Answer Evaluation

✅ Technical Score

✅ Communication Score

✅ Confidence Score

✅ Final Report
""")

# ---------------------------------
# INPUTS
# ---------------------------------
uploaded_file = st.file_uploader(
    "Upload Resume",
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

# ---------------------------------
# RESUME
# ---------------------------------
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

    # ANALYZE
    if st.button("Analyze Resume"):

        with st.spinner("Analyzing Resume..."):

            summary = summarize_resume(resume_text)

        st.subheader("Resume Analysis")
        st.markdown(summary)

    # QUESTIONS
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
        st.session_state.scores = []

        st.success("Questions Generated")

# ---------------------------------
# INTERVIEW
# ---------------------------------
if st.session_state.questions:

    st.header("Interview Session")

    idx = st.session_state.current_question

    if idx < len(st.session_state.questions):

        question = st.session_state.questions[idx]

        st.subheader(
            f"Question {idx+1} / {len(st.session_state.questions)}"
        )

        st.info(question)

        answer = st.text_area(
            "Your Answer",
            height=200,
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

                    tech = re.search(
                        r"Technical Accuracy:\s*(\d+)",
                        result
                    )

                    comm = re.search(
                        r"Communication:\s*(\d+)",
                        result
                    )

                    conf = re.search(
                        r"Confidence:\s*(\d+)",
                        result
                    )

                    if tech and comm and conf:

                        tech_score = int(
                            tech.group(1)
                        )

                        comm_score = int(
                            comm.group(1)
                        )

                        conf_score = int(
                            conf.group(1)
                        )

                        overall = round(
                            (
                                tech_score
                                + comm_score
                                + conf_score
                            ) / 3,
                            2
                        )

                        st.metric(
                            "Technical",
                            f"{tech_score}/10"
                        )
                        st.progress(
                            tech_score * 10
                        )

                        st.metric(
                            "Communication",
                            f"{comm_score}/10"
                        )
                        st.progress(
                            comm_score * 10
                        )

                        st.metric(
                            "Confidence",
                            f"{conf_score}/10"
                        )
                        st.progress(
                            conf_score * 10
                        )

                        st.metric(
                            "Overall",
                            f"{overall}/10"
                        )

                        st.session_state.scores.append(
                            overall
                        )

                else:
                    st.warning(
                        "Please enter an answer."
                    )

        with col2:

            if st.button("Next Question"):

                st.session_state.current_question += 1
                st.rerun()

    else:

        st.success(
            "Interview Completed 🎉"
        )

        st.balloons()

        if st.session_state.scores:

            avg_score = round(
                sum(
                    st.session_state.scores
                )
                /
                len(
                    st.session_state.scores
                ),
                2
            )

            st.header(
                "Final Interview Report"
            )

            st.metric(
                "Overall Score",
                f"{avg_score}/10"
            )

            if avg_score >= 8:
                st.success(
                    "Excellent Candidate"
                )

            elif avg_score >= 6:
                st.warning(
                    "Good Candidate"
                )

            else:
                st.error(
                    "Needs Improvement"
                )

            report = f"""
AI INTERVIEW REPORT

Overall Score:
{avg_score}/10

Questions Attempted:
{len(st.session_state.scores)}

Generated using Gemini AI.
"""

            st.download_button(
                "📥 Download Report",
                report,
                file_name="Interview_Report.txt"
            )
