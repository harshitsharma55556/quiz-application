import streamlit as st
import json
import os
import time

# --- Configuration & Constants ---
DATA_FILE = "quiz_data.json"

DEFAULT_QUESTIONS = [
    {
        "q": "What is the output of print(2 ** 3) in Python?",
        "options": ["6", "8", "9", "12"],
        "ans": "8"
    },
    {
        "q": "Which SQL command is used to extract data from a database?",
        "options": ["EXTRACT", "SELECT", "GET", "OPEN"],
        "ans": "SELECT"
    },
    {
        "q": "What does 'VLOOKUP' stand for in Excel?",
        "options": ["Vertical Lookup", "Value Lookup", "Variable Lookup", "View Lookup"],
        "ans": "Vertical Lookup"
    }
]

# --- Data Management Functions ---

def load_questions():
    """Load questions from a JSON file or fallback to defaults."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_QUESTIONS
    return DEFAULT_QUESTIONS


def save_questions(questions):
    """Persist questions into a JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(questions, f, indent=4)


# --- State Initialization ---

def init_session_state():
    """Initialize necessary session variables."""

    if "questions" not in st.session_state:
        st.session_state.questions = load_questions()

    if "step" not in st.session_state:
        st.session_state.step = 0

    if "score" not in st.session_state:
        st.session_state.score = 0

    if "quiz_finished" not in st.session_state:
        st.session_state.quiz_finished = False

    if "student_name" not in st.session_state:
        st.session_state.student_name = ""

    if "start_time" not in st.session_state:
        st.session_state.start_time = None


def reset_quiz():
    """Reset the student quiz progress."""

    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.start_time = None
    st.session_state.student_name = ""


# --- UI Modules ---

def render_admin_dashboard():
    """Admin panel for adding, viewing, and deleting questions."""

    st.header("Teacher / Admin Dashboard")

    with st.expander("Add a New Question", expanded=True):

        with st.form("add_question_form", clear_on_submit=True):

            new_q = st.text_input("Question Text:")

            col1, col2 = st.columns(2)

            with col1:
                opt1 = st.text_input("Option 1")
                opt2 = st.text_input("Option 2")

            with col2:
                opt3 = st.text_input("Option 3")
                opt4 = st.text_input("Option 4")

            correct_opt = st.selectbox(
                "Select Correct Answer:",
                [opt1, opt2, opt3, opt4]
            )

            submitted = st.form_submit_button("Add Question")

            if submitted:

                options = [
                    opt.strip()
                    for opt in [opt1, opt2, opt3, opt4]
                    if opt.strip()
                ]

                if new_q.strip() and len(options) >= 2:

                    st.session_state.questions.append({
                        "q": new_q.strip(),
                        "options": options,
                        "ans": correct_opt.strip()
                    })

                    save_questions(st.session_state.questions)

                    st.success("Question successfully added!")

                    st.rerun()

                else:
                    st.error(
                        "Please provide a question and at least 2 valid options."
                    )

    st.subheader(
        f"Current Questions Bank ({len(st.session_state.questions)})"
    )

    for idx, item in enumerate(st.session_state.questions):

        cols = st.columns([4, 1])

        with cols[0]:
            st.markdown(
                f"**Q{idx + 1}: {item['q']}**"
            )

            st.caption(
                f"Options: {', '.join(item['options'])} | "
                f"Correct: `{item['ans']}`"
            )

        with cols[1]:

            if st.button("Delete", key=f"del_{idx}"):

                st.session_state.questions.pop(idx)

                save_questions(st.session_state.questions)

                st.rerun()


def render_student_quiz():
    """Student view for attempting the quiz."""

    st.header("Student Quiz Portal")

    # Ask for student name before starting
    if not st.session_state.student_name:

        name = st.text_input("Enter your name:")

        if st.button("Start Quiz"):

            if name.strip():

                st.session_state.student_name = name.strip()

                # Start timer
                st.session_state.start_time = time.time()

                st.rerun()

            else:
                st.warning("Please enter your name.")

        return

    # Display student name
    st.write(
        f"Student: **{st.session_state.student_name}**"
    )

    # Calculate timer
    elapsed = int(
        time.time() - st.session_state.start_time
    )

    remaining = 300 - elapsed

    minutes = remaining // 60
    seconds = remaining % 60

    st.write(
        f"Time Remaining: {minutes:02d}:{seconds:02d}"
    )

    # Finish quiz when time is over
    if remaining <= 0:

        st.session_state.quiz_finished = True

        st.rerun()

    questions = st.session_state.questions

    if not questions:

        st.warning(
            "No questions available. Please contact the administrator."
        )

        return

    # Quiz questions
    if not st.session_state.quiz_finished:

        current_idx = st.session_state.step

        total_q = len(questions)

        # Progress bar
        st.progress(current_idx / total_q)

        st.caption(
            f"Question {current_idx + 1} of {total_q}"
        )

        current_q = questions[current_idx]

        st.subheader(current_q["q"])

        choice = st.radio(
            "Select an answer:",
            current_q["options"],
            key=f"q_{current_idx}"
        )

        if st.button("Submit Answer"):

            if choice == current_q["ans"]:

                st.session_state.score += 1

            if current_idx + 1 < total_q:

                st.session_state.step += 1

            else:

                st.session_state.quiz_finished = True

            st.rerun()

    # Final result
    else:
     st.success("Quiz Completed!")
     st.write(f"Student: **{st.session_state.student_name}**")

     total = len(questions)
    score = st.session_state.score
    percentage = (score / total) * 100

    st.metric(
        label="Final Score",
        value=f"{score} / {total}",
        delta=f"{percentage:.1f}%"
    )

    st.write(f"Correct Answers: {score}")
    st.write(f"Incorrect Answers: {st.session_state.incorrect}")

    if st.button("Retake Quiz"):
        reset_quiz()
        st.rerun()

        reset_quiz()

        st.rerun()


# --- Main Application Controller ---

def main():

    st.set_page_config(
        page_title="Dynamic Quiz Platform",
        layout="centered"
    )

    init_session_state()

    st.sidebar.title("Navigation")

    role = st.sidebar.radio(
        "Select Role:",
        ["Student Portal", "Admin Dashboard"]
    )

    if role == "Admin Dashboard":

        render_admin_dashboard()

    else:

        render_student_quiz()


if __name__ == "__main__":
    main()