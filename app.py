import csv
import io
import html
import json
import os
import random
import time
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "quiz_data.json"
RESULTS_FILE = BASE_DIR / "quiz_results.json"
DEFAULT_QUESTIONS = [
    {"q": "What is the output of print(2 ** 3) in Python?", "options": ["6", "8", "9", "12"], "ans": "8", "category": "Python", "difficulty": "Easy", "explanation": "The ** operator raises a number to a power: 2 × 2 × 2 = 8."},
    {"q": "Which SQL command is used to extract data from a database?", "options": ["EXTRACT", "SELECT", "GET", "OPEN"], "ans": "SELECT", "category": "Databases", "difficulty": "Easy", "explanation": "SELECT reads rows from one or more database tables."},
    {"q": "What does 'VLOOKUP' stand for in Excel?", "options": ["Vertical Lookup", "Value Lookup", "Variable Lookup", "View Lookup"], "ans": "Vertical Lookup", "category": "Excel", "difficulty": "Easy", "explanation": "VLOOKUP searches vertically in the first column of a range."},
]

st.set_page_config(page_title="Quizly · Learn with confidence", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#f2f4ff; --muted:#a0a6c2; --panel:#171a2b; --panel2:#20243a; --line:rgba(255,255,255,.09); --violet:#a78bfa; --mint:#73e2c1; }
.stApp { background: radial-gradient(ellipse at 80% -5%, rgba(116,82,210,.23), transparent 35%), #0e1020; color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#121426; border-right:1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:var(--muted); }
h1,h2,h3 { font-family:'Manrope','DM Sans',sans-serif !important; letter-spacing:-.04em; }
h1 { font-size:2.5rem !important; }
.hero { padding:2rem 2.2rem; border:1px solid var(--line); border-radius:24px; background:linear-gradient(120deg,rgba(116,82,210,.24),rgba(33,38,63,.84)); margin-bottom:1.4rem; }
.hero-kicker { color:var(--mint); font-size:.78rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
.hero h1 { margin:.55rem 0 .4rem; }
.hero p { color:#c3c7df; margin:0; font-size:1.04rem; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:1.35rem; }
.question-card { background:linear-gradient(145deg,#1b1e32,#151728); border:1px solid var(--line); border-radius:24px; padding:1.7rem; margin:.8rem 0 1rem; }
.eyebrow { color:var(--violet); font-size:.78rem; text-transform:uppercase; letter-spacing:.11em; font-weight:800; }
.pill { display:inline-block; background:#27253d; color:#d7caff; border:1px solid #514477; padding:.22rem .65rem; border-radius:999px; font-size:.77rem; margin-right:.35rem; }
div.stButton > button,div.stDownloadButton > button { border-radius:12px; border:1px solid var(--line); font-weight:700; min-height:2.7rem; }
div.stButton > button[kind="primary"] { background:linear-gradient(100deg,#8b68e8,#6f5bd3); border:0; }
[data-testid="stMetric"] { background:var(--panel); border:1px solid var(--line); padding:1rem 1.15rem; border-radius:16px; }
[data-testid="stMetricValue"] { color:var(--mint); }
[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#8e6ae9,#73e2c1); }
hr { border-color:var(--line); }
.small-muted { color:var(--muted); font-size:.9rem; }
</style>
""", unsafe_allow_html=True)


def normalize_question(item):
    if not isinstance(item, dict):
        return None
    question = str(item.get("q", "")).strip()
    options = list(dict.fromkeys(str(o).strip() for o in item.get("options", []) if str(o).strip()))
    answer = str(item.get("ans", "")).strip()
    if not question or len(options) < 2 or answer not in options:
        return None
    try:
        points = max(1, min(10, int(item.get("points", 1))))
    except (TypeError, ValueError):
        points = 1
    return {
        "id": str(item.get("id") or uuid.uuid4()), "q": question, "options": options,
        "ans": answer, "category": str(item.get("category", "General")).strip() or "General",
        "difficulty": str(item.get("difficulty", "Medium")),
        "explanation": str(item.get("explanation", "")).strip(),
        "points": points,
    }


def load_json(path, fallback):
    try:
        with path.open("r", encoding="utf-8") as source:
            data = json.load(source)
        return data if isinstance(data, list) else fallback
    except (OSError, json.JSONDecodeError):
        return fallback


def save_json(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def load_questions():
    raw = load_json(DATA_FILE, DEFAULT_QUESTIONS)
    questions = [q for q in (normalize_question(x) for x in raw) if q]
    return questions or [normalize_question(q) for q in DEFAULT_QUESTIONS]


def load_results():
    return load_json(RESULTS_FILE, [])


def save_questions():
    save_json(DATA_FILE, st.session_state.questions)


def reset_attempt():
    for key in ("attempt", "answers", "marked", "submitted", "review", "attempt_started", "attempt_deadline", "final_result"):
        st.session_state.pop(key, None)


def init_state():
    if "questions" not in st.session_state:
        st.session_state.questions = load_questions()
    if "results" not in st.session_state:
        st.session_state.results = load_results()
    if "page" not in st.session_state:
        st.session_state.page = "Take a quiz"


def start_attempt(name, selected, minutes, shuffle):
    questions = list(selected)
    if shuffle:
        random.shuffle(questions)
    st.session_state.attempt = questions
    st.session_state.answers = {}
    st.session_state.marked = set()
    st.session_state.submitted = False
    st.session_state.review = False
    st.session_state.attempt_started = time.time()
    st.session_state.attempt_deadline = time.time() + minutes * 60 if minutes else None
    st.session_state.student_name = name.strip()
    st.session_state.final_result = None
    st.session_state.question_index = 0


def finish_attempt(auto=False):
    if st.session_state.submitted:
        return
    questions = st.session_state.attempt
    answers = st.session_state.answers
    earned = sum(q["points"] for q in questions if answers.get(q["id"]) == q["ans"])
    possible = sum(q["points"] for q in questions)
    elapsed = max(0, int(time.time() - st.session_state.attempt_started))
    result = {
        "id": str(uuid.uuid4()), "name": st.session_state.student_name,
        "date": datetime.now().astimezone().isoformat(timespec="minutes"),
        "score": earned, "total": possible, "percentage": round(100 * earned / possible) if possible else 0,
        "correct": sum(answers.get(q["id"]) == q["ans"] for q in questions),
        "answered": sum(q["id"] in answers for q in questions),
        "questions": len(questions), "seconds": elapsed, "timed_out": auto,
        "details": [{"q": q["q"], "answer": answers.get(q["id"]), "correct_answer": q["ans"], "is_correct": answers.get(q["id"]) == q["ans"], "explanation": q["explanation"]} for q in questions],
    }
    st.session_state.results.insert(0, result)
    save_json(RESULTS_FILE, st.session_state.results[:500])
    st.session_state.final_result = result
    st.session_state.submitted = True


def hero(kicker, title, subtitle):
    st.markdown(f'<section class="hero"><div class="hero-kicker">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></section>', unsafe_allow_html=True)


def render_setup():
    hero("YOUR NEXT WIN STARTS HERE", "Ready when you are.", "Pick a topic, set your pace, and show what you know.")
    questions = st.session_state.questions
    if not questions:
        st.info("The question bank is empty. Ask your teacher to add questions.")
        return
    categories = sorted({q["category"] for q in questions})
    with st.form("quiz_setup"):
        st.subheader("Build your session")
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            name = st.text_input("Your name", placeholder="e.g. Alex Morgan")
            category = st.selectbox("Topic", ["All topics"] + categories)
        with c2:
            difficulty = st.selectbox("Difficulty", ["Any difficulty", "Easy", "Medium", "Hard"])
            count = st.selectbox("Questions", ["All available", 5, 10, 15, 20])
        with c3:
            duration = st.selectbox("Time limit", [0, 5, 10, 15, 20, 30], format_func=lambda x: "No limit" if x == 0 else f"{x} minutes")
            shuffle = st.toggle("Shuffle questions", value=True)
        start = st.form_submit_button("Start quiz  →", type="primary", use_container_width=True)
    if start:
        pool = [q for q in questions if (category == "All topics" or q["category"] == category) and (difficulty == "Any difficulty" or q["difficulty"] == difficulty)]
        if not name.strip():
            st.error("Enter your name to begin.")
        elif not pool:
            st.warning("No questions match those filters. Try a different topic or difficulty.")
        else:
            if shuffle:
                random.shuffle(pool)
            if count != "All available":
                pool = pool[:int(count)]
            start_attempt(name, pool, duration, False)
            st.rerun()
    st.markdown("#### In this question bank")
    a, b, c = st.columns(3)
    a.metric("Questions", len(questions))
    b.metric("Topics", len(categories))
    c.metric("Your past attempts", len([r for r in st.session_state.results if r.get("name", "").casefold() == st.session_state.get("student_name", "").casefold()]))


@st.fragment(run_every="1s")
def render_active_quiz():
    questions = st.session_state.attempt
    index = st.session_state.get("question_index", 0)
    if st.session_state.attempt_deadline:
        remaining = int(st.session_state.attempt_deadline - time.time())
        if remaining <= 0:
            finish_attempt(auto=True)
            st.rerun()
        mins, secs = divmod(remaining, 60)
    else:
        elapsed = int(time.time() - st.session_state.attempt_started)
        mins, secs = divmod(elapsed, 60)
    answered_count = sum(q["id"] in st.session_state.answers for q in questions)
    top = st.columns([2, 1, 1])
    with top[0]:
        st.markdown(f"**{st.session_state.student_name}** <span class='small-muted'>· {answered_count}/{len(questions)} answered</span>", unsafe_allow_html=True)
    with top[1]:
        st.metric("Time left" if st.session_state.attempt_deadline else "Elapsed", f"{mins:02d}:{secs:02d}")
    with top[2]:
        st.metric("Marked", len(st.session_state.marked))
    st.progress(answered_count / len(questions), text=f"{answered_count} of {len(questions)} answered")
    q = questions[index]
    st.markdown(f"<div class='question-card'><div class='eyebrow'>QUESTION {index+1:02d} / {len(questions):02d}</div><h2>{html.escape(q['q'])}</h2><span class='pill'>{html.escape(q['category'])}</span><span class='pill'>{html.escape(q['difficulty'])}</span><span class='pill'>{q['points']} point{'s' if q['points'] != 1 else ''}</span></div>", unsafe_allow_html=True)
    current = st.session_state.answers.get(q["id"])
    chosen = st.radio("Choose one answer", q["options"], index=q["options"].index(current) if current in q["options"] else None, key=f"answer_{q['id']}", label_visibility="collapsed")
    st.session_state.answers[q["id"]] = chosen if chosen else st.session_state.answers.get(q["id"])
    nav = st.columns([1, 1, 2, 1, 1])
    with nav[0]:
        if st.button("← Previous", disabled=index == 0, use_container_width=True):
            st.session_state.question_index -= 1
            st.rerun()
    with nav[1]:
        mark_label = "★ Marked" if q["id"] in st.session_state.marked else "☆ Mark for review"
        if st.button(mark_label, use_container_width=True):
            if q["id"] in st.session_state.marked:
                st.session_state.marked.remove(q["id"])
            else:
                st.session_state.marked.add(q["id"])
            st.rerun()
    with nav[3]:
        if st.button("Next →", disabled=index == len(questions)-1, type="primary", use_container_width=True):
            st.session_state.question_index += 1
            st.rerun()
    with nav[4]:
        if st.button("Finish quiz", use_container_width=True):
            st.session_state.review = True
            st.rerun()
    with st.expander("Jump to a question"):
        cols = st.columns(min(10, len(questions)))
        for i, item in enumerate(questions):
            with cols[i % len(cols)]:
                label = ("★ " if item["id"] in st.session_state.marked else "") + str(i+1)
                if st.button(label, key=f"jump_{i}", type="primary" if i == index else "secondary", use_container_width=True):
                    st.session_state.question_index = i
                    st.rerun()
    if st.session_state.review:
        unanswered = len(questions) - answered_count
        st.warning(f"You have {unanswered} unanswered question(s) and {len(st.session_state.marked)} marked for review.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Back to quiz", use_container_width=True):
                st.session_state.review = False
                st.rerun()
        with c2:
            if st.button("Submit my answers", type="primary", use_container_width=True):
                finish_attempt()
                st.rerun()


def render_results():
    result = st.session_state.final_result
    if not result:
        render_setup()
        return
    pct = result["percentage"]
    message, emoji = ("Outstanding work!", "🏆") if pct >= 90 else ("Great progress!", "✨") if pct >= 70 else ("Keep going — practice builds confidence.", "🌱")
    hero(f"{emoji}  {message.upper()}", f"{pct}% — quiz complete", f"Nice work, {result['name']}. Here’s how you did.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Points", f"{result['score']} / {result['total']}")
    c2.metric("Correct", result["correct"])
    c3.metric("Answered", f"{result['answered']} / {result['questions']}")
    c4.metric("Time", f"{result['seconds']//60}m {result['seconds']%60:02d}s")
    st.progress(pct / 100, text=f"Your score: {pct}%")
    with st.expander("Review every answer", expanded=True):
        for i, item in enumerate(result["details"], 1):
            icon = "✅" if item["is_correct"] else "❌"
            st.markdown(f"**{icon} {i}. {item['q']}**")
            st.caption(f"Your answer: {item['answer'] or 'Not answered'} · Correct answer: {item['correct_answer']}")
            if item["explanation"]:
                st.info(item["explanation"])
    if result["timed_out"]:
        st.warning("Time ran out. Your answers were submitted automatically.")
    if st.button("Take another quiz", type="primary"):
        reset_attempt()
        st.rerun()


def render_quiz():
    if st.session_state.get("attempt") and not st.session_state.submitted:
        render_active_quiz()
    elif st.session_state.get("submitted"):
        render_results()
    else:
        render_setup()


def render_question_bank():
    hero("TEACHER STUDIO", "Question bank", "Create, organize and review the questions in your class quiz.")
    questions = st.session_state.questions
    tab_add, tab_manage, tab_import = st.tabs(["＋ Add a question", "☷ Manage bank", "⇧ Import / export"])
    with tab_add:
        with st.form("add_question", clear_on_submit=True):
            prompt = st.text_area("Question", placeholder="Write a clear question…")
            c1,c2 = st.columns(2)
            with c1:
                opts = [st.text_input(f"Option {i+1}", key=f"new_opt_{i}") for i in range(4)]
                category = st.text_input("Topic", value="General")
            with c2:
                correct = st.selectbox("Correct answer", ["Option 1", "Option 2", "Option 3", "Option 4"])
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
                points = st.number_input("Points", 1, 10, 1)
            explanation = st.text_area("Explanation (shown after submission)", placeholder="Optional learning note")
            add = st.form_submit_button("Add to question bank", type="primary")
        if add:
            valid_opts = list(dict.fromkeys(o.strip() for o in opts if o.strip()))
            selected_text = opts[int(correct.split()[-1])-1].strip()
            if not prompt.strip() or len(valid_opts) < 2 or not selected_text:
                st.error("Add a question, at least two options, and select a filled correct option.")
            else:
                q = normalize_question({"q":prompt,"options":valid_opts,"ans":selected_text,"category":category,"difficulty":difficulty,"points":points,"explanation":explanation})
                st.session_state.questions.append(q)
                save_questions()
                st.success("Question added.")
                st.rerun()
    with tab_manage:
        query = st.text_input("Search questions", placeholder="Search by question, topic or answer")
        cats = sorted({q["category"] for q in questions})
        selected_cat = st.selectbox("Filter topic", ["All topics"] + cats, key="manage_category")
        visible = [(i,q) for i,q in enumerate(questions) if (not query or query.casefold() in " ".join([q["q"],q["category"],q["ans"]]).casefold()) and (selected_cat == "All topics" or q["category"] == selected_cat)]
        st.caption(f"Showing {len(visible)} of {len(questions)} questions")
        for i, q in visible:
            with st.expander(f"{i+1}. {q['q']} · {q['category']} / {q['difficulty']}"):
                st.write("Options: " + " · ".join(q["options"]))
                st.write(f"Correct answer: **{q['ans']}** · {q['points']} point(s)")
                if q["explanation"]: st.caption(q["explanation"])
                e1,e2 = st.columns(2)
                with e1:
                    if st.button("Edit", key=f"edit_{q['id']}"):
                        st.session_state.edit_question = q["id"]
                with e2:
                    if st.button("Delete", key=f"delete_{q['id']}"):
                        st.session_state.questions.pop(i)
                        save_questions()
                        st.rerun()
        edit_id = st.session_state.get("edit_question")
        edit_q = next((q for q in questions if q["id"] == edit_id), None)
        if edit_q:
            st.markdown("#### Edit question")
            with st.form("edit_question_form"):
                prompt = st.text_area("Question", edit_q["q"])
                opts = [st.text_input(f"Option {i+1}", value=edit_q["options"][i] if i < len(edit_q["options"]) else "", key=f"editopt{i}") for i in range(4)]
                answer_idx = edit_q["options"].index(edit_q["ans"])
                correct = st.selectbox("Correct answer", ["Option 1","Option 2","Option 3","Option 4"], index=answer_idx)
                category = st.text_input("Topic", edit_q["category"])
                difficulty = st.selectbox("Difficulty", ["Easy","Medium","Hard"], index=["Easy","Medium","Hard"].index(edit_q["difficulty"]) if edit_q["difficulty"] in ["Easy","Medium","Hard"] else 1)
                points = st.number_input("Points",1,10,edit_q["points"])
                explanation = st.text_area("Explanation",edit_q["explanation"])
                saved = st.form_submit_button("Save changes",type="primary")
            if saved:
                valid_opts = list(dict.fromkeys(o.strip() for o in opts if o.strip()))
                answer = opts[int(correct.split()[-1])-1].strip()
                updated = normalize_question({**edit_q,"q":prompt,"options":valid_opts,"ans":answer,"category":category,"difficulty":difficulty,"points":points,"explanation":explanation})
                if updated:
                    st.session_state.questions[next(i for i,x in enumerate(questions) if x["id"] == edit_id)] = updated
                    save_questions(); st.session_state.pop("edit_question",None); st.success("Question updated."); st.rerun()
                else: st.error("Check the question, options and correct answer.")
    with tab_import:
        st.markdown("Import questions from JSON using the same `q`, `options`, `ans` fields as the existing file. Optional fields: `category`, `difficulty`, `explanation`, `points`.")
        upload = st.file_uploader("Choose a JSON question file", type=["json"])
        mode = st.radio("Import mode", ["Add to current bank", "Replace current bank"], horizontal=True)
        if upload and st.button("Import questions", type="primary"):
            try:
                parsed = json.loads(upload.getvalue().decode("utf-8"))
                if not isinstance(parsed, list): raise ValueError("The file must contain a JSON list.")
                imported = [normalize_question(item) for item in parsed]
                imported = [item for item in imported if item]
                if not imported: raise ValueError("No valid questions were found. Each needs a prompt, two options and a correct answer.")
                st.session_state.questions = (questions + imported) if mode.startswith("Add") else imported
                save_questions(); st.success(f"Imported {len(imported)} question(s)."); st.rerun()
            except (ValueError, UnicodeDecodeError) as error:
                st.error(str(error))
        payload = json.dumps(questions, indent=2, ensure_ascii=False)
        st.download_button("Download question bank (JSON)", payload, file_name="quiz_questions.json", mime="application/json")
        if st.button("Restore the original sample questions"):
            st.session_state.questions = [normalize_question(q) for q in DEFAULT_QUESTIONS]
            save_questions(); st.success("Sample question bank restored."); st.rerun()


def render_analytics():
    hero("TEACHER STUDIO", "Results & insights", "See recent attempts and how the class is progressing.")
    results = st.session_state.results
    if not results:
        st.info("Results will appear here after the first quiz attempt.")
        return
    avg = round(sum(r.get("percentage",0) for r in results) / len(results))
    c1,c2,c3 = st.columns(3)
    c1.metric("Total attempts",len(results)); c2.metric("Average score",f"{avg}%"); c3.metric("Unique students",len({r.get('name','').casefold() for r in results}))
    st.subheader("Recent attempts")
    for r in results[:100]:
        with st.expander(f"{r.get('name','Student')} · {r.get('percentage',0)}% · {r.get('date','')}"):
            c1,c2,c3 = st.columns(3)
            c1.write(f"**Score:** {r.get('score',0)} / {r.get('total',0)}")
            c2.write(f"**Correct:** {r.get('correct',0)} / {r.get('questions',0)}")
            c3.write(f"**Time:** {r.get('seconds',0)//60}m {r.get('seconds',0)%60:02d}s")
    csv_buffer = io.StringIO()
    if results:
        writer = csv.DictWriter(csv_buffer, fieldnames=["name","date","percentage","score","total","correct","answered","questions","seconds","timed_out"])
        writer.writeheader()
        for r in results: writer.writerow({k:r.get(k) for k in writer.fieldnames})
    st.download_button("Download results (CSV)",csv_buffer.getvalue(),file_name="quiz_results.csv",mime="text/csv")
    if st.button("Clear all saved results"):
        st.session_state.results=[]; save_json(RESULTS_FILE,[]); st.success("Results cleared."); st.rerun()


def main():
    init_state()
    with st.sidebar:
        st.markdown("# ✦ Quizly")
        st.caption("A calmer way to test what you know.")
        st.divider()
        page = st.radio("Navigate", ["Take a quiz", "Question bank", "Results & insights"], label_visibility="collapsed", key="page")
        st.divider()
        st.markdown(f"**{len(st.session_state.questions)}** questions · **{len(st.session_state.results)}** attempts")
        st.caption("Teacher studio tools are available in Question bank and Results.")
    if page == "Take a quiz": render_quiz()
    elif page == "Question bank": render_question_bank()
    else: render_analytics()


if __name__ == "__main__":
    main()


