import csv
import hashlib
import hmac
import html
import io
import json
import random
import re
import secrets
import time
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LEGACY_FILE = BASE_DIR / "quiz_data.json"
QUIZZES_FILE = BASE_DIR / "quizzes.json"
ACCOUNTS_FILE = BASE_DIR / "accounts.json"
RESULTS_FILE = BASE_DIR / "quiz_results.json"
PASSWORD_ROUNDS = 310_000
DEFAULT_QUESTIONS = [
    {"q": "What is the output of print(2 ** 3) in Python?", "options": ["6", "8", "9", "12"], "ans": "8", "category": "Python", "difficulty": "Easy", "explanation": "The ** operator raises a number to a power: 2 × 2 × 2 = 8."},
    {"q": "Which SQL command is used to extract data from a database?", "options": ["EXTRACT", "SELECT", "GET", "OPEN"], "ans": "SELECT", "category": "Databases", "difficulty": "Easy", "explanation": "SELECT reads rows from one or more database tables."},
    {"q": "What does 'VLOOKUP' stand for in Excel?", "options": ["Vertical Lookup", "Value Lookup", "Variable Lookup", "View Lookup"], "ans": "Vertical Lookup", "category": "Excel", "difficulty": "Easy", "explanation": "VLOOKUP searches vertically in the first column of a range."},
]

PYTHON_QUESTIONS = [
    {"q": "What is printed by print(2 + 3 * 2)?", "options": ["10", "8", "13", "7"], "ans": "8", "category": "Python", "difficulty": "Easy", "explanation": "Multiplication happens before addition, so 2 + (3 × 2) equals 8."},
    {"q": "What does colors[1] return when colors = ['red', 'blue', 'green']?", "options": ["red", "blue", "green", "An error"], "ans": "blue", "category": "Python", "difficulty": "Easy", "explanation": "Python lists use zero-based indexing, so index 1 is the second item."},
    {"q": "What is the value of len('quiz')?", "options": ["3", "4", "5", "It depends"], "ans": "4", "category": "Python", "difficulty": "Easy", "explanation": "len returns the number of characters in the string. 'quiz' has four characters."},
    {"q": "What is the result of 5 > 3 and 2 < 1?", "options": ["True", "False", "2", "An error"], "ans": "False", "category": "Python", "difficulty": "Medium", "explanation": "The first comparison is true, but the second is false. With and, both conditions must be true."},
    {"q": "What does list(range(3)) produce?", "options": ["[1, 2, 3]", "[0, 1, 2]", "[0, 1, 2, 3]", "[3]"], "ans": "[0, 1, 2]", "category": "Python", "difficulty": "Easy", "explanation": "range(3) starts at zero and stops before three."},
    {"q": "Which expression reads the value for the key 'name' from a dictionary called student?", "options": ["student.name", "student('name')", "student['name']", "student->name"], "ans": "student['name']", "category": "Python", "difficulty": "Medium", "explanation": "Square brackets with the key retrieve a value from a dictionary."},
    {"q": "Which keyword starts a function definition in Python?", "options": ["function", "func", "def", "define"], "ans": "def", "category": "Python", "difficulty": "Easy", "explanation": "Python uses the def keyword followed by the function name."},
    {"q": "What is int('12') + 3?", "options": ["123", "15", "12.3", "An error"], "ans": "15", "category": "Python", "difficulty": "Easy", "explanation": "int converts the text '12' to the integer 12, then 3 is added."},
    {"q": "What is type(3.14).__name__?", "options": ["int", "str", "float", "decimal"], "ans": "float", "category": "Python", "difficulty": "Easy", "explanation": "A number written with a decimal point is a float in Python."},
    {"q": "Which built-in collection can be changed after it is created?", "options": ["tuple", "string", "list", "integer"], "ans": "list", "category": "Python", "difficulty": "Medium", "explanation": "Lists are mutable, which means you can add, remove, or replace their items."},
]
st.set_page_config(page_title="Quizly | Classroom", page_icon=str(BASE_DIR / "quizly.svg"), layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Montserrat:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&display=swap');
:root { --ink:#20223a; --muted:#70738a; --line:#e9e9f1; --violet:#6753d8; --paper:#f6f6fb; }
.stApp { background:radial-gradient(ellipse at 78% -8%,rgba(133,112,236,.15),transparent 34%),var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:var(--muted); }
h1,h2,h3,h4 { font-family:'Manrope','DM Sans',sans-serif !important; letter-spacing:-.04em; color:var(--ink); }
h1 { font-size:2.5rem !important; font-weight:800 !important; }
.hero { padding:2rem 2.2rem; border:1px solid #e7e3fa; border-radius:26px; background:linear-gradient(118deg,#fff 12%,#f0edff); margin-bottom:1.5rem; box-shadow:0 12px 35px #382d780e; }
.hero-kicker,.eyebrow { color:var(--violet); font-size:.76rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
.hero h1 { margin:.55rem 0 .4rem; }.hero p { color:#686b82; margin:0; font-size:1.05rem; }
.brand-mark { display:inline-flex; align-items:center; justify-content:center; width:38px; height:38px; border-radius:13px; background:linear-gradient(140deg,#8975f0,#5c48c8); color:white; font-size:1.2rem; }
.quiz-card { min-height:165px; padding:1.4rem; background:#fff; border:1px solid var(--line); border-radius:21px; box-shadow:0 10px 26px #2826460b; }
.question-card { background:linear-gradient(145deg,#fff,#f4f2ff); border:1px solid #e8e3fb; border-radius:24px; padding:1.7rem; margin:.8rem 0 1rem; box-shadow:0 12px 26px #332c670f; }
.pill { display:inline-block; background:#f0edff; color:#5848b2; border:1px solid #e3ddff; padding:.25rem .7rem; border-radius:999px; font-size:.77rem; margin-right:.35rem; font-weight:700; }
div.stButton > button,div.stDownloadButton > button { border-radius:12px; border:1px solid var(--line); font-weight:700; min-height:2.7rem; }
div.stButton > button[kind="primary"] { background:linear-gradient(100deg,#7762e4,#5c49c8); border:0; color:white; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:1rem 1.1rem; border-radius:17px; box-shadow:0 7px 18px #28264609; }
[data-testid="stMetricValue"] { color:var(--violet); font-family:'Manrope',sans-serif; font-weight:800; }
[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#8e7af0,#54cda7); }
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea { border-radius:11px; }
hr { border-color:var(--line); }.small-muted { color:var(--muted); font-size:.9rem; }
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { color:#20223a !important; }
.block-container { box-sizing:border-box; width:100%; max-width:1440px !important; margin:0 auto !important; padding:2.5rem clamp(1.25rem,4vw,4rem) 4rem !important; }
.stApp { overflow-x:hidden; }
p,label,legend,[data-testid="stWidgetLabel"] p,[data-testid="stMarkdownContainer"] { color:#20223a; }
[data-testid="stWidgetLabel"] p { font-weight:600; }
[data-baseweb="tab"] { color:#686b82 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:#6753d8 !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color:#6753d8 !important; }
[data-baseweb="input"] > div,[data-baseweb="textarea"] { background:#fff !important; border-color:#dedee9 !important; }
[data-baseweb="input"] input,[data-baseweb="textarea"] textarea { color:#20223a !important; caret-color:#6753d8; }
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder { color:#9294a5 !important; }
div.stButton > button[kind="primary"],div[data-testid="stFormSubmitButton"] button,button[kind="primaryFormSubmit"] { background:linear-gradient(100deg,#7762e4,#5c49c8) !important; color:#fff !important; border:0 !important; }
[data-testid="stForm"] { border:0; }
@media (max-width:700px) { .block-container { padding:1.25rem 1rem 3rem !important; } h1 { font-size:2rem !important; } }
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,label,legend { color:#20223a !important; }
.stTabs button[data-baseweb="tab"] { color:#686b82 !important; }
.stTabs button[data-baseweb="tab"][aria-selected="true"] { color:#6753d8 !important; }
.stTabs [data-baseweb="tab-highlight"],[data-baseweb="tab-border"] { background:#6753d8 !important; }
button[kind*="primary"],div[data-testid="stFormSubmitButton"] button { background:linear-gradient(100deg,#7762e4,#5c49c8) !important; color:#fff !important; border:0 !important; }
/* Larger, calmer typography and Figma-inspired login role cards */
body,.stApp,[data-testid="stWidgetLabel"] p,label,p { font-size:1.05rem; }
h1 { font-size:2.8rem !important; }
h2 { font-size:1.95rem !important; }
h3 { font-size:1.4rem !important; }
[data-testid="stWidgetLabel"] p,label { font-weight:600 !important; }
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea { font-size:1.05rem !important; min-height:3.2rem; }
div.stButton > button,div.stDownloadButton > button { font-size:1.02rem !important; min-height:3.1rem !important; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:20px !important; border-color:#e5e2f3 !important; background:#fff; box-shadow:0 9px 25px #30286b0b; }
.login-title { font-family:'Manrope','DM Sans',sans-serif; font-size:3.1rem !important; line-height:1.06; margin:1.4rem 0 1rem; }
.login-copy { color:#666a82 !important; font-size:1.18rem !important; line-height:1.65; max-width:38rem; }
.login-stat { margin-top:2rem; padding:1rem 1.2rem; display:inline-block; border-radius:16px; background:#fff; border:1px solid #e8e4f5; color:#666a82; }
.login-stat strong { color:#6753d8; font-size:1.5rem; font-family:'Manrope',sans-serif; }
@media (max-width:700px) { .login-title { font-size:2.35rem !important; } h1 { font-size:2.2rem !important; } body,p,label { font-size:1rem; } }
/* Quizly visual system inspired by editorial tech landing pages */
:root { --ink:#07113f; --muted:#566284; --line:#dfe7f3; --violet:#05b8dc; --paper:#f3f7fc; --navy:#050638; --blue:#063e91; --cyan:#18c6e5; }
.stApp { background:#f4f7fc !important; color:#07113f !important; font-family:'Source Sans 3','Segoe UI',sans-serif !important; }
.block-container { max-width:1600px !important; padding:0 clamp(1rem,4vw,4rem) 4rem !important; }
h1,h2,h3,h4 { color:#07113f !important; font-family:'Montserrat','Segoe UI',sans-serif !important; letter-spacing:-.025em !important; }
h1 { font-size:2.8rem !important; } h2 { font-size:2rem !important; } h3 { font-size:1.42rem !important; }
p,label,[data-testid="stWidgetLabel"] p { font-family:'Source Sans 3','Segoe UI',sans-serif !important; font-size:1.08rem !important; }
.brandbar { height:82px; margin:0 calc(-1 * clamp(1rem,4vw,4rem)); padding:0 clamp(1.4rem,9vw,9rem); background:#050638; color:#fff; display:flex; align-items:center; justify-content:space-between; gap:2rem; }
.brand-lockup { display:flex; align-items:center; gap:1rem; color:#fff; }.brand-logo { width:46px; height:46px; border:2px solid #13c6e1; border-radius:4px 15px 4px 15px; display:grid; place-items:center; font:800 1.35rem 'Montserrat',sans-serif; color:#fff; box-shadow:inset 0 0 0 4px #ffffff10; }
.brand-name { color:#fff; font:800 1.45rem 'Montserrat',sans-serif; letter-spacing:.02em; }.brand-tag { border-left:1px solid #64709c; padding-left:1rem; color:#b8c4e7; font:700 .78rem 'Montserrat',sans-serif; letter-spacing:.1em; line-height:1.5; text-transform:uppercase; }
.brand-actions { color:#fff; display:flex; align-items:center; gap:2rem; font:700 .9rem 'Montserrat',sans-serif; letter-spacing:.1em; text-transform:uppercase; }.brand-actions .accent { color:#25c8e3; }
.public-nav { height:58px; margin:0 calc(-1 * clamp(1rem,4vw,4rem)); padding:0 clamp(1.4rem,9vw,9rem); background:#fff; border-bottom:1px solid #e0e7f2; display:flex; align-items:center; gap:clamp(1rem,4vw,4rem); color:#091143; font:700 .84rem 'Montserrat',sans-serif; letter-spacing:.1em; text-transform:uppercase; }
.landing-hero { position:relative; overflow:hidden; min-height:390px; margin:0 calc(-1 * clamp(1rem,4vw,4rem)); padding:3.3rem clamp(1.4rem,9vw,9rem); color:#fff; background:radial-gradient(ellipse at 80% 18%,#05abd0 0,transparent 32%),linear-gradient(112deg,#071145 0%,#064a9f 57%,#078fc5 100%); }
.landing-hero:before { content:''; position:absolute; inset:0; opacity:.25; background-image:radial-gradient(#5ce4f6 1.7px,transparent 1.7px); background-size:19px 19px; mask-image:linear-gradient(90deg,#000,transparent 34%); }
.landing-inner { position:relative; z-index:1; display:flex; align-items:center; justify-content:space-between; gap:2rem; max-width:1450px; margin:auto; }.landing-copy { max-width:780px; }
.landing-kicker { color:#70e3e7; font:800 .86rem 'Montserrat',sans-serif; letter-spacing:.15em; text-transform:uppercase; }
.landing-title { margin:1.1rem 0 1rem; color:#fff !important; font:4.5rem/1.02 'DM Serif Display',Georgia,serif !important; letter-spacing:-.02em !important; }.landing-title em { color:#53dfd1; font-style:normal; }
.landing-subtitle { color:#e2edff !important; max-width:660px; font:500 1.25rem/1.55 'Source Sans 3',sans-serif !important; }.landing-stats { margin-top:1.4rem; color:#fff; font:700 .9rem 'Montserrat',sans-serif; letter-spacing:.09em; text-transform:uppercase; }.landing-stats strong { color:#65e2d3; }
.landing-art { width:340px; height:240px; position:relative; flex:0 0 340px; display:grid; place-items:center; }.art-glow { position:absolute; width:220px; height:220px; border-radius:50%; background:linear-gradient(140deg,#2bd2e1aa,#4d63ff44); filter:blur(4px); }
.art-card { position:relative; width:260px; padding:1.3rem; border:1px solid #9ae8f877; border-radius:19px; background:linear-gradient(145deg,#0a1b62ef,#082c78df); box-shadow:0 22px 50px #0005; transform:rotate(-5deg); color:#fff; }.art-card small { color:#70e3e7; font:700 .72rem 'Montserrat',sans-serif; letter-spacing:.12em; }.art-score { margin:.45rem 0; font:3.2rem 'DM Serif Display',Georgia,serif; }.art-progress { height:8px; background:#ffffff33; border-radius:9px; overflow:hidden; }.art-progress span { display:block; width:78%; height:100%; background:linear-gradient(90deg,#25cce0,#70e3d2); }.art-chip { position:absolute; right:0; bottom:12px; padding:.75rem 1rem; background:#fff; border-radius:12px; color:#07113f; font:700 .85rem 'Montserrat',sans-serif; box-shadow:0 9px 22px #0003; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px !important; border-color:#dfe7f3 !important; background:#fff; box-shadow:0 9px 25px #06184a0e; }
.quiz-card { border-color:#dfe7f3; box-shadow:0 12px 30px #07113f0c; }.question-card { background:linear-gradient(145deg,#fff,#f1f8ff); border-color:#cceaf3; }
.hero { color:#fff !important; padding:2.6rem 3rem; border:0; border-radius:4px 24px 4px 24px; background:radial-gradient(ellipse at 85% 20%,#09acd0,transparent 36%),linear-gradient(110deg,#071145,#075aa8); box-shadow:0 17px 35px #06184a22; }
.hero h1,.hero h2,.hero p { color:#fff !important; }.hero h1 { font:3.4rem/1.08 'DM Serif Display',Georgia,serif !important; letter-spacing:0 !important; }.hero-kicker,.eyebrow { color:#4edbd9 !important; font-size:.8rem; }.pill { background:#e8fbfd; color:#075682; border-color:#c7f0f5; }
[data-testid="stMetric"] { border-color:#dce9f5; }.stProgress > div > div { background:linear-gradient(90deg,#03b7de,#48dfc9) !important; }
@media(max-width:850px) { .brand-tag,.brand-actions span:first-child { display:none; }.public-nav { overflow-x:auto; white-space:nowrap; }.landing-inner { align-items:flex-start; }.landing-title { font-size:3.5rem !important; }.landing-art { width:230px; flex-basis:230px; transform:scale(.85); transform-origin:center right; } }
@media(max-width:620px) { .brandbar { height:68px; }.brand-actions { gap:.7rem; font-size:.72rem; }.public-nav { height:48px; font-size:.68rem; }.landing-hero { padding:2.5rem 1.3rem; }.landing-inner { display:block; }.landing-title { font-size:3rem !important; }.landing-art { display:none; }.hero { padding:2rem 1.3rem; }.hero h1 { font-size:2.5rem !important; } }
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"] { display:none !important; }
/* Clean, high-contrast portal cards and login form */
.section-kicker { margin-top:1.5rem; color:#0a9dbb; font:800 .78rem 'Montserrat',sans-serif; letter-spacing:.16em; }
.portal-title { margin:.3rem 0 .25rem; color:#07113f !important; font:800 2rem 'Montserrat',sans-serif !important; }
.role-heading { display:flex; align-items:center; gap:.85rem; color:#09143c; font:800 1.3rem 'Montserrat',sans-serif; margin:.2rem 0 .7rem; }

[data-testid="stVerticalBlockBorderWrapper"] { padding:1rem !important; border:1px solid #dbe5f0 !important; border-radius:20px !important; background:linear-gradient(145deg,#fff,#f8fbff) !important; box-shadow:0 14px 32px #07113f12 !important; }
[data-testid="stForm"] { max-width:760px; margin:1rem auto !important; padding:1.5rem !important; border:1px solid #dbe5f0 !important; border-radius:18px !important; background:#fff !important; box-shadow:0 14px 34px #07113f10 !important; }
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="input"] input,[data-baseweb="textarea"] textarea { background:#fff !important; color:#111b3e !important; font-size:1.08rem !important; border-radius:12px !important; }
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus { border-color:#12b8d3 !important; box-shadow:0 0 0 3px #12b8d322 !important; }
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,label,legend { color:#172348 !important; }
[data-testid="stCaptionContainer"] p { color:#626d88 !important; }
div.stButton > button { background:#fff !important; color:#0b1942 !important; border:1px solid #cbd7e7 !important; border-radius:12px !important; font:700 1rem 'Montserrat',sans-serif !important; min-height:3.2rem !important; }
div.stButton > button:hover { background:#effbff !important; border-color:#12b8d3 !important; color:#065f83 !important; }
div.stButton > button[kind*="primary"],div[data-testid="stFormSubmitButton"] button[kind*="primary"],button[kind*="primary"] { background:linear-gradient(105deg,#08afd0,#087dc0) !important; color:#fff !important; border:0 !important; }
button[kind*="primary"] *,div[data-testid="stFormSubmitButton"] button * { color:#fff !important; }
input[type="radio"] { accent-color:#0aaec8 !important; }
/* Quiz flow: soft lilac canvas, layered purple panels, white answer cards */
.stApp { background:radial-gradient(ellipse at 8% 4%,#f0cfff 0,transparent 30%),radial-gradient(ellipse at 94% 74%,#e8d6ff 0,transparent 27%),#f7f2ff !important; }
.hero { background:radial-gradient(ellipse at 88% 12%,#bd70ed,transparent 38%),linear-gradient(118deg,#7b36c7,#9c50dc 60%,#a65bda) !important; border-radius:28px !important; box-shadow:0 18px 42px #7436a32c !important; }
.hero .hero-kicker,.hero .eyebrow { color:#f4dcff !important; }
.question-card { background:#fff !important; border:1px solid #eee1fa !important; border-radius:24px !important; box-shadow:0 14px 34px #63379216 !important; }
.quiz-question-panel { padding:1.5rem 1.7rem; margin:.65rem 0 1rem; border:1px solid #ead9f7; border-radius:26px; background:#fff; box-shadow:0 18px 44px #63379218; }
.quiz-question-meta { display:flex; justify-content:space-between; align-items:center; color:#8950bc; font:700 .8rem 'Montserrat',sans-serif; letter-spacing:.11em; text-transform:uppercase; }
.quiz-question-text { margin:1.1rem 0 1.5rem; color:#24203c; font:700 1.75rem/1.35 'Montserrat',sans-serif; letter-spacing:-.03em; }
.quiz-tag { display:inline-block; margin-right:.45rem; padding:.35rem .75rem; border-radius:999px; color:#78509a; background:#f5eaff; border:1px solid #ead8f7; font:700 .75rem 'Montserrat',sans-serif; }
.quiz-side-card { padding:1.4rem; margin:.65rem 0 1rem; border:1px solid #ead9f7; border-radius:24px; background:linear-gradient(160deg,#fff,#fbf6ff); box-shadow:0 14px 32px #63379214; }
.quiz-side-title { margin-bottom:1rem; color:#312345; font:800 1.15rem 'Montserrat',sans-serif; }
.score-ring { width:168px; height:168px; margin:.4rem auto 1rem; border-radius:50%; display:grid; place-items:center; background:conic-gradient(#9e51d2 var(--score),#eeddf8 var(--score)); box-shadow:0 8px 20px #8c50b222; }
.score-ring-inner { width:134px; height:134px; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#fff; color:#3d2a52; }
.score-ring-label { color:#8b55b4; font:700 .85rem 'Montserrat',sans-serif; }.score-ring-value { font:800 2.4rem 'Montserrat',sans-serif; letter-spacing:-.05em; }.score-ring-unit { color:#9a86a8; font:600 .75rem 'Montserrat',sans-serif; }
.leader-row { display:grid; grid-template-columns:38px 1fr auto; align-items:center; gap:.65rem; padding:.65rem .2rem; border-top:1px solid #f0e8f6; color:#4b4056; }
.leader-rank { width:30px; height:30px; display:grid; place-items:center; border-radius:50%; background:#f1e4fb; color:#8545b6; font:800 .78rem 'Montserrat',sans-serif; }
.leader-row:first-child .leader-rank { background:#8545b6; color:#fff; }.leader-name { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:700; }.leader-score { color:#80509f; font:700 .8rem 'Montserrat',sans-serif; }
.leader-current { color:#7d3eb1; background:#f8efff; border-radius:10px; padding:.2rem .4rem; font:700 .62rem 'Montserrat',sans-serif; }
.quiz-meta-strip { display:flex; gap:1.2rem; align-items:center; padding:.85rem 1rem; border:1px solid #e8d9f5; border-radius:16px; background:#fff; color:#6b5d78; font:700 .84rem 'Montserrat',sans-serif; }
[data-testid="stMetric"] { border-color:#eadcf4 !important; box-shadow:0 10px 24px #6337920d !important; }
[data-testid="stMetricValue"] { color:#8751bb !important; }
[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#8c42c7,#c072e9) !important; }
[data-testid="stRadio"] [role="radiogroup"] label { padding:.55rem .75rem; margin:.35rem 0; border:1px solid #eee2f7; border-radius:13px; background:#fff; font-weight:600; }
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) { border-color:#a65bd4; background:#f7edff; box-shadow:0 0 0 2px #a65bd422; }
@media(max-width:700px) { .quiz-question-text { font-size:1.35rem; }.quiz-question-panel,.quiz-side-card { padding:1rem; }.score-ring { width:140px;height:140px; }.score-ring-inner { width:112px;height:112px; } }
/* Student workspace: polished quiz discovery, progress, and motion */
.student-intro { display:flex; align-items:flex-end; justify-content:space-between; gap:2rem; padding:2.1rem 2.4rem; margin:1.35rem 0 1.2rem; border:1px solid #e5e7f4; border-radius:26px; background:radial-gradient(ellipse at 88% 5%,#d8ccff 0,transparent 35%),linear-gradient(120deg,#fff,#f3f0ff 70%,#edfaff); box-shadow:0 18px 48px #10174712; }
.student-intro-copy { max-width:760px; }.student-intro-kicker { color:#7455c7; font:800 .75rem 'Montserrat',sans-serif; letter-spacing:.16em; text-transform:uppercase; }.student-intro h1 { margin:.55rem 0 .45rem; font:800 clamp(2rem,4vw,3.1rem)/1.08 'Montserrat',sans-serif !important; letter-spacing:-.055em !important; }.student-intro p { color:#62708d; font-size:1.08rem !important; margin:0; }
.student-focus { min-width:180px; padding:1rem 1.2rem; border:1px solid #ffffffb8; border-radius:18px; background:#ffffffa8; backdrop-filter:blur(12px); }.student-focus strong { display:block; color:#261c5c; font:800 1.65rem 'Montserrat',sans-serif; }.student-focus span { color:#70738a; font-size:.9rem; }
.student-section-title { margin:.2rem 0 .25rem; font:800 1.55rem 'Montserrat',sans-serif; color:#111b44; letter-spacing:-.04em; }.student-section-copy { color:#74809a; margin:0 0 1rem; }
.student-toolbar { padding:1rem 1.1rem .4rem; margin:.8rem 0 1.1rem; border:1px solid #e5eaf3; border-radius:20px; background:#ffffffd9; box-shadow:0 12px 30px #17224a0a; }
.student-quiz-card { position:relative; overflow:hidden; min-height:210px; padding:1.35rem 1.4rem 1.2rem; margin:.15rem 0 .2rem; border:1px solid #e3e8f3; border-radius:22px; background:linear-gradient(145deg,#fff,#fbfcff); box-shadow:0 12px 30px #12234c0b; transition:transform .24s ease,box-shadow .24s ease,border-color .24s ease; }
.student-quiz-card:before { content:''; position:absolute; width:110px; height:110px; border-radius:50%; top:-65px; right:-23px; background:linear-gradient(135deg,#e6dcff,#d8f7f7); opacity:.8; }
.student-quiz-card:hover { transform:translateY(-4px); border-color:#b8a9ee; box-shadow:0 20px 38px #30236217; }
.student-quiz-top { position:relative; display:flex; justify-content:space-between; align-items:center; gap:.8rem; }.student-topic { color:#6a51bd; font:800 .7rem 'Montserrat',sans-serif; letter-spacing:.13em; text-transform:uppercase; }.student-status { padding:.3rem .65rem; border:1px solid #d9f0e8; border-radius:999px; background:#effaf5; color:#287a61; font:700 .68rem 'Montserrat',sans-serif; }
.student-quiz-card h3 { position:relative; margin:.8rem 0 .4rem; font:800 1.3rem 'Montserrat',sans-serif !important; letter-spacing:-.035em !important; }.student-quiz-card p { position:relative; min-height:2.9rem; margin:0 0 .85rem; color:#69758d; font-size:.96rem !important; line-height:1.5; }.student-card-meta { position:relative; display:flex; flex-wrap:wrap; gap:.45rem; }.student-card-meta span { padding:.32rem .65rem; border:1px solid #e6e9f1; border-radius:999px; background:#f7f8fc; color:#4c5875; font:700 .7rem 'Montserrat',sans-serif; }
.student-card-progress { position:relative; display:flex; justify-content:space-between; gap:.6rem; margin-top:.85rem; color:#78839a; font-size:.78rem; }.student-card-progress strong { color:#6449bd; }
.student-start div.stButton > button { border-radius:0 0 17px 17px !important; margin-top:-.25rem; min-height:3.25rem !important; transition:filter .2s ease,letter-spacing .2s ease,transform .2s ease; }.student-start div.stButton > button:hover { filter:brightness(1.05); letter-spacing:.025em; transform:translateY(-1px); }
.student-empty { padding:2rem; border:1px dashed #cbd3e3; border-radius:20px; background:#ffffffb5; color:#69758d; text-align:center; }
.student-intro ~ div div.stButton > button { transition:transform .2s ease,box-shadow .2s ease,background .2s ease; }
.student-intro ~ div div.stButton > button:hover { transform:translateY(-2px); box-shadow:0 7px 18px #3225641b; }
div[class*="st-key-student_quiz_filter"] [role="radiogroup"] { display:flex; flex-wrap:wrap; gap:.25rem; width:max-content; max-width:100%; padding:.32rem; border:1px solid #e5e6ef; border-radius:999px; background:#f0f1f7; }
div[class*="st-key-student_quiz_filter"] [role="radiogroup"] label { margin:0 !important; padding:.52rem .9rem !important; border:1px solid transparent !important; border-radius:999px !important; background:transparent !important; transition:color .22s ease,background .22s ease,box-shadow .22s ease,transform .22s ease; }
div[class*="st-key-student_quiz_filter"] [role="radiogroup"] label:has(input:checked) { border-color:#e7e0fb !important; background:#fff !important; color:#4e3aa4 !important; box-shadow:0 3px 10px #25204b14 !important; transform:translateY(-1px); }
@media(max-width:760px) { .student-intro { display:block; padding:1.5rem; }.student-focus { margin-top:1.2rem; }.student-quiz-card { min-height:0; } }
</style>
""", unsafe_allow_html=True)


def load_json(path, fallback):
    try:
        with path.open("r", encoding="utf-8-sig") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError):
        return fallback


def save_json(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def normalize_question(item):
    if not isinstance(item, dict):
        return None
    prompt = str(item.get("q", "")).strip()
    options = list(dict.fromkeys(str(x).strip() for x in item.get("options", []) if str(x).strip()))
    answer = str(item.get("ans", "")).strip()
    if not prompt or len(options) < 2 or answer not in options:
        return None
    try:
        points = max(1, min(10, int(item.get("points", 1))))
    except (TypeError, ValueError):
        points = 1
    return {"id": str(item.get("id") or uuid.uuid4()), "q": prompt, "options": options, "ans": answer,
            "category": str(item.get("category", "General")).strip() or "General",
            "difficulty": str(item.get("difficulty", "Medium")),
            "explanation": str(item.get("explanation", "")).strip(), "points": points}


def load_quizzes():
    stored = load_json(QUIZZES_FILE, None)
    if isinstance(stored, list):
        return stored
    legacy = load_json(LEGACY_FILE, DEFAULT_QUESTIONS)
    source = legacy if isinstance(legacy, list) else DEFAULT_QUESTIONS
    questions = [x for x in (normalize_question(q) for q in source) if x]
    if not questions:
        questions = [normalize_question(q) for q in DEFAULT_QUESTIONS]
    quizzes = [
        {"id": str(uuid.uuid4()), "title": "Starter Quiz",
         "description": "A short warm-up across Python, databases, and Excel.",
         "duration_minutes": 5, "shuffle": True, "published": True,
         "questions": questions},
        {"id": str(uuid.uuid4()), "title": "Python Fundamentals",
         "description": "Practice Python expressions, lists, dictionaries, functions, and built-in types.",
         "duration_minutes": 10, "shuffle": True, "published": True,
         "questions": [normalize_question(q) for q in PYTHON_QUESTIONS]},
    ]
    save_json(QUIZZES_FILE, quizzes)
    return quizzes


def init_state():
    # Refresh the quiz bank from disk on each app rerun so newly published quizzes appear
    # in active student sessions without requiring a new browser session.
    st.session_state.quizzes = load_quizzes()
    if "accounts" not in st.session_state:
        data = load_json(ACCOUNTS_FILE, [])
        st.session_state.accounts = data if isinstance(data, list) else []
    if "results" not in st.session_state:
        data = load_json(RESULTS_FILE, [])
        st.session_state.results = data if isinstance(data, list) else []
    if "user" not in st.session_state:
        st.session_state.user = None


def save_quizzes():
    save_json(QUIZZES_FILE, st.session_state.quizzes)


def save_accounts():
    save_json(ACCOUNTS_FILE, st.session_state.accounts)


def save_results():
    save_json(RESULTS_FILE, st.session_state.results[:1000])


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PASSWORD_ROUNDS).hex()


def create_account(username, password, role):
    salt = secrets.token_hex(16)
    return {"username": username, "username_key": username.casefold(), "role": role,
            "salt": salt, "password_hash": password_hash(password, salt)}


def verify_account(username, password):
    key = username.strip().casefold()
    account = next((a for a in st.session_state.accounts if a.get("username_key") == key), None)
    if not account:
        return None
    return account if hmac.compare_digest(password_hash(password, account["salt"]), account["password_hash"]) else None


def validate_account(username, password, confirm):
    username = username.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,24}", username):
        return "Use a username with 3–24 letters, numbers, dots, dashes, or underscores."
    if len(password) < 8:
        return "Choose a password with at least 8 characters."
    if password != confirm:
        return "The passwords don’t match."
    return ""


def reset_attempt():
    for key in ("attempt", "answers", "marked", "submitted", "review", "attempt_started", "attempt_deadline", "final_result", "question_index"):
        st.session_state.pop(key, None)


def hero(kicker, title, subtitle):
    st.markdown(f'<section class="hero"><div class="hero-kicker">{html.escape(kicker)}</div><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></section>', unsafe_allow_html=True)


def render_auth():
    published = sum(bool(q.get("published")) for q in st.session_state.quizzes)
    st.markdown('''<header class="brandbar"><div class="brand-lockup"><div class="brand-logo">Q</div><div class="brand-name">QUIZLY</div><div class="brand-tag">LEARN +<br>GROW</div></div></header>''', unsafe_allow_html=True)
    st.markdown('''<nav class="public-nav"><span>STUDENT QUIZZES</span><span>LEARNING PROGRESS</span><span>TEACHER STUDIO</span><span>BUILD · PRACTICE · GROW</span></nav>''', unsafe_allow_html=True)
    st.markdown(f'''<section class="landing-hero"><div class="landing-inner"><div class="landing-copy"><div class="landing-kicker">A CLASSROOM FOR CURIOSITY</div><h1 class="landing-title">Learn. <em>Grow.</em><br>Show what you know.</h1><p class="landing-subtitle">Take thoughtful quizzes from your teacher, build confidence with every answer, and keep your progress in view.</p><div class="landing-stats"><strong>{published}</strong> PUBLISHED QUIZZES &nbsp;·&nbsp; <strong>2</strong> SPACES TO LEARN</div></div><div class="landing-art"><div class="art-glow"></div><div class="art-card"><small>YOUR NEXT CHALLENGE</small><div class="art-score">Ready?</div><div class="art-progress"><span></span></div><small>ONE QUESTION AT A TIME</small></div><div class="art-chip">KEEP GROWING</div></div></div></section>''', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">SIGN IN TO QUIZLY</div><h2 class="portal-title">Choose your portal</h2>', unsafe_allow_html=True)
    st.caption("Select a role to continue to your account.")
    role = st.session_state.get("auth_role", "student")
    student_col, teacher_col = st.columns(2, gap="medium")
    with student_col:
        with st.container(border=True):
            st.markdown('<div class="role-heading"><span>Student Login</span></div>', unsafe_allow_html=True)
            st.caption("Take published quizzes and follow your scores.")
            if st.button("Student Login", key="select_student", type="primary" if role == "student" else "secondary", use_container_width=True):
                st.session_state.auth_role = "student"
                st.rerun()
    with teacher_col:
        with st.container(border=True):
            st.markdown('<div class="role-heading"><span>Admin Login</span></div>', unsafe_allow_html=True)
            st.caption("Create quizzes, publish them, and review class results.")
            if st.button("Admin Login", key="select_teacher", type="primary" if role == "admin" else "secondary", use_container_width=True):
                st.session_state.auth_role = "admin"
                st.rerun()
    if role == "student":
        mode = st.session_state.get("student_auth_mode", "Sign in")
        sign_in_col, create_col = st.columns(2, gap="small")
        with sign_in_col:
            if st.button("Sign in", key="student_mode_signin", type="primary" if mode == "Sign in" else "secondary", use_container_width=True):
                st.session_state.student_auth_mode = "Sign in"
                st.rerun()
        with create_col:
            if st.button("Create student account", key="student_mode_create", type="primary" if mode == "Create student account" else "secondary", use_container_width=True):
                st.session_state.student_auth_mode = "Create student account"
                st.rerun()
        if mode == "Sign in":
            with st.form("student_login"):
                username = st.text_input("Username", key="s_login_user")
                password = st.text_input("Password", type="password", key="s_login_pass")
                submit = st.form_submit_button("Sign in as student", type="primary", use_container_width=True)
            if submit:
                account = verify_account(username, password)
                if account and account["role"] == "student":
                    st.session_state.user = account
                    st.session_state.page = "Available quizzes"
                    st.rerun()
                st.error("We couldn’t sign you in as a student. Check your details or create an account.")
        else:
            with st.form("student_signup"):
                username = st.text_input("Choose a username", key="s_signup_user", help="3–24 letters, numbers, dots, dashes, or underscores")
                password = st.text_input("Create a password", type="password", key="s_signup_pass", help="At least 8 characters")
                confirm = st.text_input("Confirm password", type="password", key="s_signup_confirm")
                submit = st.form_submit_button("Create student account", type="primary", use_container_width=True)
            if submit:
                error = validate_account(username, password, confirm)
                if error:
                    st.error(error)
                elif any(a.get("username_key") == username.strip().casefold() for a in st.session_state.accounts):
                    st.error("That username is already taken.")
                else:
                    st.session_state.accounts.append(create_account(username.strip(), password, "student"))
                    save_accounts()
                    st.success("Account created. Choose Sign in to continue.")
    else:
        first_admin = not any(a.get("role") == "admin" for a in st.session_state.accounts)
        if first_admin:
            st.info("First-time setup: create the teacher account for this app. This option closes after the first admin is created.")
            with st.form("admin_setup"):
                username = st.text_input("Teacher username", key="a_setup_user")
                password = st.text_input("Create teacher password", type="password", key="a_setup_pass")
                confirm = st.text_input("Confirm password", type="password", key="a_setup_confirm")
                submit = st.form_submit_button("Create teacher account", type="primary", use_container_width=True)
            if submit:
                error = validate_account(username, password, confirm)
                if error:
                    st.error(error)
                elif any(a.get("username_key") == username.strip().casefold() for a in st.session_state.accounts):
                    st.error("That username is already taken.")
                else:
                    st.session_state.accounts.append(create_account(username.strip(), password, "admin"))
                    save_accounts()
                    st.success("Teacher account created. Sign in below.")
                    st.rerun()
        else:
            with st.form("admin_login"):
                username = st.text_input("Teacher username", key="a_login_user")
                password = st.text_input("Password", type="password", key="a_login_pass")
                submit = st.form_submit_button("Admin Login", type="primary", use_container_width=True)
            if submit:
                account = verify_account(username, password)
                if account and account["role"] == "admin":
                    st.session_state.user = account
                    st.session_state.page = "Quiz studio"
                    st.rerun()
                st.error("We couldn’t sign you in as an admin. Check your teacher account details.")

def logout():
    reset_attempt()
    st.session_state.user = None
    st.rerun()


def start_attempt(quiz):
    questions = list(quiz.get("questions", []))
    if quiz.get("shuffle", True):
        random.shuffle(questions)
    st.session_state.attempt = questions
    st.session_state.attempt_quiz_id = quiz["id"]
    st.session_state.attempt_quiz_title = quiz["title"]
    st.session_state.answers = {}
    st.session_state.marked = set()
    st.session_state.submitted = False
    st.session_state.review = False
    st.session_state.attempt_started = time.time()
    minutes = int(quiz.get("duration_minutes", 0))
    st.session_state.attempt_deadline = time.time() + minutes * 60 if minutes else None
    st.session_state.final_result = None
    st.session_state.question_index = 0


def finish_attempt(auto=False):
    if st.session_state.submitted:
        return
    questions, answers = st.session_state.attempt, st.session_state.answers
    earned = sum(q["points"] for q in questions if answers.get(q["id"]) == q["ans"])
    possible = sum(q["points"] for q in questions)
    elapsed = max(0, int(time.time() - st.session_state.attempt_started))
    user = st.session_state.user
    result = {
        "id": str(uuid.uuid4()), "name": user["username"], "username_key": user["username_key"],
        "quiz_id": st.session_state.attempt_quiz_id, "quiz_title": st.session_state.attempt_quiz_title,
        "date": datetime.now().astimezone().isoformat(timespec="minutes"), "score": earned, "total": possible,
        "percentage": round(100 * earned / possible) if possible else 0,
        "correct": sum(answers.get(q["id"]) == q["ans"] for q in questions),
        "answered": sum(q["id"] in answers for q in questions), "questions": len(questions),
        "seconds": elapsed, "timed_out": auto,
        "details": [{"q": q["q"], "answer": answers.get(q["id"]), "correct_answer": q["ans"], "is_correct": answers.get(q["id"]) == q["ans"], "explanation": q["explanation"]} for q in questions],
    }
    st.session_state.results.insert(0, result)
    save_results()
    st.session_state.final_result = result
    st.session_state.submitted = True


def render_student_home():
    user = st.session_state.user
    quizzes = [q for q in st.session_state.quizzes if q.get("published") and q.get("questions")]
    mine = [r for r in st.session_state.results if r.get("username_key") == user["username_key"]]
    completed_ids = {r.get("quiz_id") for r in mine}
    best_by_quiz = {}
    for result in mine:
        key = result.get("quiz_id")
        best_by_quiz[key] = max(best_by_quiz.get(key, 0), int(result.get("percentage", 0)))
    average = round(sum(int(r.get("percentage", 0)) for r in mine) / len(mine)) if mine else 0
    st.markdown(
        f"<section class='student-intro'><div class='student-intro-copy'><div class='student-intro-kicker'>YOUR LEARNING SPACE</div>"
        f"<h1>Good to see you, {html.escape(user['username'])}.</h1><p>Pick up a new challenge, build your streak, and keep your progress moving.</p></div>"
        f"<div class='student-focus'><strong>{len(quizzes)} ready</strong><span>Published quizzes to explore</span></div></section>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='student-section-title'>Your learning at a glance</div>", unsafe_allow_html=True)
    stats = st.columns(4, gap="medium")
    stats[0].metric("Available quizzes", len(quizzes))
    stats[1].metric("Quizzes tried", len(completed_ids))
    stats[2].metric("Attempts", len(mine))
    stats[3].metric("Average score", f"{average}%" if mine else "—")
    if not quizzes:
        st.markdown("<div class='student-empty'><strong>No quizzes published yet</strong><br>When your teacher makes one available, it will appear here.</div>", unsafe_allow_html=True)
        return
    st.markdown("<div class='student-section-title'>Explore quizzes</div><p class='student-section-copy'>Find a topic, choose your pace, and jump back in whenever you’re ready.</p>", unsafe_allow_html=True)
    with st.container(border=True):
        search_col, topic_col, sort_col = st.columns([1.55, 1, 1], gap="medium")
        search = search_col.text_input("Search quizzes", placeholder="Search by title or topic", key="student_quiz_search", label_visibility="collapsed")
        topics = sorted({str(question.get("category", "General")) for quiz in quizzes for question in quiz.get("questions", [])})
        selected_topic = topic_col.selectbox("Topic", ["All topics", *topics], key="student_quiz_topic", label_visibility="collapsed")
        sort_by = sort_col.selectbox("Sort", ["Recommended", "Title A–Z", "Shortest first", "Most questions"], key="student_quiz_sort", label_visibility="collapsed")
    view_filter = st.radio("Quiz status", ["All quizzes", "Not started", "Completed"], horizontal=True, key="student_quiz_filter", label_visibility="collapsed")
    query = search.strip().casefold()
    visible = []
    for quiz in quizzes:
        title = str(quiz.get("title", "Untitled quiz"))
        description = str(quiz.get("description", ""))
        quiz_topics = {str(question.get("category", "General")) for question in quiz.get("questions", [])}
        if query and query not in f"{title} {description} {' '.join(quiz_topics)}".casefold():
            continue
        if selected_topic != "All topics" and selected_topic not in quiz_topics:
            continue
        if view_filter == "Completed" and quiz["id"] not in completed_ids:
            continue
        if view_filter == "Not started" and quiz["id"] in completed_ids:
            continue
        visible.append(quiz)
    if sort_by == "Title A–Z":
        visible.sort(key=lambda quiz: str(quiz.get("title", "")).casefold())
    elif sort_by == "Shortest first":
        visible.sort(key=lambda quiz: (int(quiz.get("duration_minutes", 0) or 0) or 999, len(quiz.get("questions", []))))
    elif sort_by == "Most questions":
        visible.sort(key=lambda quiz: len(quiz.get("questions", [])), reverse=True)
    st.caption(f"Showing {len(visible)} of {len(quizzes)} published quizzes")
    if not visible:
        st.markdown("<div class='student-empty'><strong>No matching quizzes</strong><br>Try another search or choose a different topic or status.</div>", unsafe_allow_html=True)
    columns = st.columns(2, gap="large")
    for i, quiz in enumerate(visible):
        with columns[i % 2]:
            title = str(quiz.get("title", "Untitled quiz"))
            questions = quiz.get("questions", [])
            quiz_topics = sorted({str(question.get("category", "General")) for question in questions})
            topic_label = quiz_topics[0] if quiz_topics else "General"
            duration = int(quiz.get("duration_minutes", 0) or 0)
            complete = quiz["id"] in completed_ids
            status = "COMPLETED" if complete else "READY TO PLAY"
            score = best_by_quiz.get(quiz["id"])
            best_line = f"Best score <strong>{score}%</strong>" if score is not None else "A fresh start is waiting"
            st.markdown(
                f"<article class='student-quiz-card'><div class='student-quiz-top'><span class='student-topic'>{html.escape(topic_label)}</span><span class='student-status'>{status}</span></div>"
                f"<h3>{html.escape(title)}</h3><p>{html.escape(str(quiz.get('description') or 'A quiz prepared by your teacher.'))}</p>"
                f"<div class='student-card-meta'><span>{len(questions)} questions</span><span>{f'{duration} min' if duration else 'No time limit'}</span><span>{len(quiz_topics)} topic{'s' if len(quiz_topics) != 1 else ''}</span></div>"
                f"<div class='student-card-progress'><span>{best_line}</span><span>{'Ready to improve' if complete else 'Start when you’re ready'}</span></div></article>",
                unsafe_allow_html=True,
            )
            button_label = "Try again  →" if complete else "Start quiz  →"
            if st.button(button_label, key=f"start_{quiz['id']}", type="primary", use_container_width=True):
                start_attempt(quiz)
                st.rerun()
    if mine:
        st.markdown("<div class='student-section-title' style='margin-top:2rem'>Recent progress</div>", unsafe_allow_html=True)
        recent_cols = st.columns(min(3, len(mine)), gap="medium")
        for col, result in zip(recent_cols, mine[:3]):
            with col:
                st.markdown(f"<div class='quiz-side-card'><div class='student-topic'>RECENT RESULT</div><div class='quiz-side-title' style='margin:.45rem 0'>{html.escape(str(result.get('quiz_title', 'Quiz')))}</div><strong style='font:800 1.6rem Montserrat;color:#7043b5'>{int(result.get('percentage',0))}%</strong><div class='small-muted'>{html.escape(str(result.get('date','')))}</div></div>", unsafe_allow_html=True)


def leaderboard_entries(quiz_id, current_user=None, current_score=0, current_total=0):
    best = {}
    for saved in st.session_state.results:
        if saved.get("quiz_id") != quiz_id:
            continue
        key = saved.get("username_key") or saved.get("name", "Student").casefold()
        if key not in best or saved.get("percentage", 0) > best[key].get("percentage", 0):
            best[key] = {"key": key, "name": saved.get("name", "Student"), "score": saved.get("score", 0), "percentage": saved.get("percentage", 0)}
    if current_user:
        key = current_user["username_key"]
        pct = round(current_score * 100 / current_total) if current_total else 0
        best[key] = {"key": key, "name": current_user["username"], "score": current_score, "percentage": pct, "current": True}
    return sorted(best.values(), key=lambda row: (-row.get("percentage", 0), -row.get("score", 0), row["name"].casefold()))[:6]


def leaderboard_markup(entries):
    if not entries:
        return "<div class='leader-empty'>Complete a quiz to start the class leaderboard.</div>"
    rows = []
    for rank, entry in enumerate(entries, 1):
        current = "<span class='leader-current'>YOU</span>" if entry.get("current") else ""
        rows.append(f"<div class='leader-row'><span class='leader-rank'>{rank}</span><span class='leader-name'>{html.escape(entry['name'])} {current}</span><span class='leader-score'>{entry['percentage']}% · {entry['score']} pt</span></div>")
    return "".join(rows)


@st.fragment(run_every="1s")
def render_active_quiz():
    questions = st.session_state.attempt
    if not questions:
        st.warning("This quiz has no questions. Please ask your teacher to update it.")
        return
    index = st.session_state.question_index
    deadline = st.session_state.attempt_deadline
    if deadline:
        remaining = int(deadline - time.time())
        if remaining <= 0:
            finish_attempt(auto=True)
            st.rerun()
        minutes, seconds = divmod(remaining, 60)
    else:
        minutes, seconds = divmod(int(time.time() - st.session_state.attempt_started), 60)
    question = questions[index]
    answered = sum(q["id"] in st.session_state.answers for q in questions)
    current_score = sum(q["points"] for q in questions if st.session_state.answers.get(q["id"]) == q["ans"])
    possible = sum(q["points"] for q in questions)
    percent = round(current_score * 100 / possible) if possible else 0

    st.markdown(f"<div class='quiz-meta-strip'><span>{html.escape(st.session_state.attempt_quiz_title)}</span><span>QUESTION {index+1:02d} / {len(questions):02d}</span><span>{answered} ANSWERED</span></div>", unsafe_allow_html=True)
    left, right = st.columns([1.55, .8], gap="large")
    with left:
        st.markdown(f"<div class='quiz-question-panel'><div class='quiz-question-meta'><span>Question {index+1:02d}</span><span>{minutes:02d}:{seconds:02d} {'left' if deadline else 'elapsed'}</span></div><h2 class='quiz-question-text'>{html.escape(question['q'])}</h2><span class='quiz-tag'>{html.escape(question['category'])}</span><span class='quiz-tag'>{html.escape(question['difficulty'])}</span><span class='quiz-tag'>{question['points']} point(s)</span></div>", unsafe_allow_html=True)
        current = st.session_state.answers.get(question["id"])
        choice = st.radio("Choose one answer", question["options"], index=question["options"].index(current) if current in question["options"] else None, key=f"answer_{question['id']}", label_visibility="collapsed")
        st.session_state.answers[question["id"]] = choice if choice else st.session_state.answers.get(question["id"])
        nav = st.columns([1, 1, 1, 1])
        if nav[0].button("Previous", disabled=index == 0, use_container_width=True):
            st.session_state.question_index -= 1
            st.rerun()
        marked = st.session_state.marked
        mark_label = "Marked for review" if question["id"] in marked else "Mark for review"
        if nav[1].button(mark_label, use_container_width=True):
            marked.remove(question["id"]) if question["id"] in marked else marked.add(question["id"])
            st.rerun()
        if nav[2].button("Next question", disabled=index == len(questions)-1, type="primary", use_container_width=True):
            st.session_state.question_index += 1
            st.rerun()
        if nav[3].button("Finish", use_container_width=True):
            st.session_state.review = True
            st.rerun()
        with st.expander("Jump to a question"):
            cols = st.columns(min(10, len(questions)))
            for i, item in enumerate(questions):
                with cols[i % len(cols)]:
                    label = ("★ " if item["id"] in marked else "") + str(i+1)
                    if st.button(label, key=f"jump_{i}", type="primary" if i == index else "secondary", use_container_width=True):
                        st.session_state.question_index = i
                        st.rerun()
        if st.session_state.review:
            st.warning(f"{len(questions)-answered} unanswered · {len(marked)} marked for review")
            back, submit = st.columns(2)
            if back.button("Continue quiz", use_container_width=True):
                st.session_state.review = False
                st.rerun()
            if submit.button("Submit my answers", type="primary", use_container_width=True):
                finish_attempt()
                st.rerun()
    with right:
        st.markdown(f"<div class='quiz-side-card'><div class='quiz-side-title'>Your score</div><div class='score-ring' style='--score:{percent}%'><div class='score-ring-inner'><span class='score-ring-label'>POINTS</span><span class='score-ring-value'>{current_score}</span><span class='score-ring-unit'>OF {possible}</span></div></div><div class='quiz-side-title'>Progress</div><div class='leader-row'><span class='leader-rank'>✓</span><span class='leader-name'>Completed</span><span class='leader-score'>{answered}/{len(questions)}</span></div><div class='leader-row'><span class='leader-rank'>○</span><span class='leader-name'>Correct so far</span><span class='leader-score'>{sum(st.session_state.answers.get(q['id']) == q['ans'] for q in questions)}</span></div><div class='leader-row'><span class='leader-rank'>★</span><span class='leader-name'>For review</span><span class='leader-score'>{len(st.session_state.marked)}</span></div></div>", unsafe_allow_html=True)
        entries = leaderboard_entries(st.session_state.attempt_quiz_id, st.session_state.user, current_score, possible)
        st.markdown(f"<div class='quiz-side-card'><div class='quiz-side-title'>Class leaderboard</div>{leaderboard_markup(entries)}</div>", unsafe_allow_html=True)


def render_results():
    result = st.session_state.final_result
    pct = result["percentage"]
    message = "Outstanding work!" if pct >= 90 else "Great progress!" if pct >= 70 else "Keep going — practice builds confidence."
    hero("QUIZ COMPLETE", f"{pct}% · {message}", f"{result['quiz_title']} · Nice work, {result['name']}.")
    main_col, side_col = st.columns([1.15, .85], gap="large")
    with main_col:
        st.markdown(f"<div class='quiz-side-card'><div class='quiz-side-title'>Your score</div><div class='score-ring' style='--score:{pct}%'><div class='score-ring-inner'><span class='score-ring-label'>TOTAL SCORE</span><span class='score-ring-value'>{result['score']}</span><span class='score-ring-unit'>OF {result['total']} POINTS</span></div></div><div class='leader-row'><span class='leader-rank'>1</span><span class='leader-name'>Correct answers</span><span class='leader-score'>{result['correct']} / {result['questions']}</span></div><div class='leader-row'><span class='leader-rank'>2</span><span class='leader-name'>Completion</span><span class='leader-score'>{result['answered']} / {result['questions']}</span></div><div class='leader-row'><span class='leader-rank'>3</span><span class='leader-name'>Time taken</span><span class='leader-score'>{result['seconds']//60}m {result['seconds']%60:02d}s</span></div></div>", unsafe_allow_html=True)
        st.progress(pct / 100, text=f"Your score: {pct}%")
    with side_col:
        entries = leaderboard_entries(result["quiz_id"], {"username": result["name"], "username_key": result["username_key"]}, result["score"], result["total"])
        st.markdown(f"<div class='quiz-side-card'><div class='quiz-side-title'>Class leaderboard</div>{leaderboard_markup(entries)}</div>", unsafe_allow_html=True)
        if result["timed_out"]:
            st.warning("Time ran out. Your answers were submitted automatically.")
        if st.button("Back to available quizzes", type="primary", use_container_width=True):
            reset_attempt()
            st.session_state.page = "Available quizzes"
            st.rerun()
    with st.expander("Review your answers", expanded=True):
        for i, item in enumerate(result["details"], 1):
            status = "CORRECT" if item["is_correct"] else "REVIEW"
            st.markdown(f"**{status} · {i}. {item['q']}**")
            st.caption(f"Your answer: {item['answer'] or 'Not answered'} · Correct answer: {item['correct_answer']}")
            if item["explanation"]:
                st.info(item["explanation"])

def render_my_results():
    hero("STUDENT SPACE", "My results", "Your quiz attempts and scores are private to your account.")
    results = [r for r in st.session_state.results if r.get("username_key") == st.session_state.user["username_key"]]
    if not results:
        st.info("Your completed quizzes will appear here.")
        return
    for result in results:
        with st.expander(f"{result.get('quiz_title','Quiz')} · {result.get('percentage',0)}% · {result.get('date','')}"):
            st.write(f"Score: **{result.get('score',0)} / {result.get('total',0)}** · Correct: **{result.get('correct',0)} / {result.get('questions',0)}**")


def render_student():
    if st.session_state.get("attempt") and not st.session_state.get("submitted"):
        render_active_quiz()
    elif st.session_state.get("submitted") and st.session_state.get("final_result"):
        render_results()
    elif st.session_state.page == "My results":
        render_my_results()
    else:
        render_student_home()


def render_quiz_studio():
    hero("TEACHER STUDIO", "Build a quiz.", "Create a draft, add questions, then publish it when students are ready.")
    with st.expander("＋ Create a new quiz", expanded=not bool(st.session_state.quizzes)):
        with st.form("create_quiz", clear_on_submit=True):
            title = st.text_input("Quiz title", placeholder="e.g. Introduction to Python")
            description = st.text_area("Description", placeholder="Tell students what this quiz covers.")
            a, b = st.columns(2)
            duration = a.selectbox("Time limit", [0, 5, 10, 15, 20, 30], format_func=lambda n: "No time limit" if n == 0 else f"{n} minutes")
            shuffle = b.toggle("Shuffle question order", value=True)
            create = st.form_submit_button("Create quiz draft", type="primary")
        if create:
            if not title.strip():
                st.error("Give your quiz a title first.")
            else:
                quiz = {"id": str(uuid.uuid4()), "title": title.strip(), "description": description.strip(),
                        "duration_minutes": duration, "shuffle": shuffle, "published": False,
                        "questions": [], "created_at": datetime.now().astimezone().isoformat(timespec="minutes")}
                st.session_state.quizzes.insert(0, quiz)
                save_quizzes()
                st.success("Draft created. Add questions below, then publish it.")
                st.rerun()
    if not st.session_state.quizzes:
        st.info("Your quiz studio is ready. Create a quiz to get started.")
        return
    st.markdown("### Your quizzes")
    for quiz in st.session_state.quizzes:
        status = "PUBLISHED" if quiz.get("published") else "DRAFT"
        with st.expander(f"{quiz['title']} · {status} · {len(quiz.get('questions', []))} questions"):
            st.caption(quiz.get("description") or "No description yet.")
            c1, c2, c3 = st.columns([1, 1, 2])
            if c1.button("Unpublish" if quiz.get("published") else "Publish quiz", key=f"pub_{quiz['id']}", type="primary" if not quiz.get("published") else "secondary", disabled=not quiz.get("questions")):
                quiz["published"] = not quiz.get("published", False)
                save_quizzes()
                st.rerun()
            if c2.button("Delete quiz", key=f"delquiz_{quiz['id']}"):
                st.session_state.quizzes = [item for item in st.session_state.quizzes if item["id"] != quiz["id"]]
                save_quizzes()
                st.rerun()
            c3.caption(f"{len(quiz.get('questions', []))} questions · {quiz.get('duration_minutes', 0) or 'No'} minute limit")
            st.markdown("#### Questions")
            for number, question in enumerate(quiz.get("questions", []), 1):
                st.markdown(f"**{number}. {question['q']}**")
                st.caption(f"{question['category']} · {question['difficulty']} · Correct answer: {question['ans']}")
            st.markdown("#### Add a question")
            with st.form(f"addq_{quiz['id']}", clear_on_submit=True):
                prompt = st.text_area("Question", key=f"prompt_{quiz['id']}")
                left, right = st.columns(2)
                with left:
                    options = [st.text_input(f"Option {i+1}", key=f"opt_{quiz['id']}_{i}") for i in range(4)]
                    category = st.text_input("Topic", value="General", key=f"cat_{quiz['id']}")
                with right:
                    correct = st.selectbox("Correct answer", [f"Option {i}" for i in range(1, 5)], key=f"ans_{quiz['id']}")
                    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key=f"diff_{quiz['id']}")
                    points = st.number_input("Points", 1, 10, 1, key=f"points_{quiz['id']}")
                explanation = st.text_area("Explanation shown after the quiz", key=f"explain_{quiz['id']}")
                add = st.form_submit_button("Add question", type="primary")
            if add:
                valid_options = list(dict.fromkeys(value.strip() for value in options if value.strip()))
                answer = options[int(correct.split()[-1])-1].strip()
                item = normalize_question({"q": prompt, "options": valid_options, "ans": answer,
                                           "category": category, "difficulty": difficulty,
                                           "points": points, "explanation": explanation})
                if not item:
                    st.error("Add a question, at least two options, and a correct option with text.")
                else:
                    quiz["questions"].append(item)
                    save_quizzes()
                    st.success("Question added to this quiz.")
                    st.rerun()


def render_class_results():
    hero("TEACHER STUDIO", "Class results", "Review quiz attempts and download a report.")
    results = st.session_state.results
    if not results:
        st.info("Results will appear here after students complete a quiz.")
        return
    avg = round(sum(r.get("percentage", 0) for r in results) / len(results))
    a, b, c = st.columns(3)
    a.metric("Total attempts", len(results))
    b.metric("Average score", f"{avg}%")
    c.metric("Students", len({r.get("username_key", r.get("name", "").casefold()) for r in results}))
    for result in results[:150]:
        title = result.get("quiz_title", "Quiz")
        with st.expander(f"{result.get('name','Student')} · {title} · {result.get('percentage',0)}% · {result.get('date','')}"):
            st.write(f"Score: **{result.get('score',0)} / {result.get('total',0)}** · Correct: **{result.get('correct',0)} / {result.get('questions',0)}** · Time: **{result.get('seconds',0)//60}m {result.get('seconds',0)%60:02d}s**")
    output = io.StringIO()
    fields = ["name", "quiz_title", "date", "percentage", "score", "total", "correct", "answered", "questions", "seconds", "timed_out"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for result in results:
        writer.writerow({key: result.get(key) for key in fields})
    st.download_button("Download class results (CSV)", output.getvalue(), file_name="quiz_results.csv", mime="text/csv")


def main():
    init_state()
    user = st.session_state.user
    if not user:
        render_auth()
        return
    username = html.escape(user["username"])
    role_label = "TEACHER STUDIO" if user["role"] == "admin" else "STUDENT SPACE"
    st.markdown(f'''<header class="brandbar"><div class="brand-lockup"><div class="brand-logo">Q</div><div class="brand-name">QUIZLY</div><div class="brand-tag">LEARN +<br>GROW</div></div><div class="brand-actions"><span>{role_label}</span><span>{username}</span></div></header>''', unsafe_allow_html=True)
    options = ["Quiz studio", "Class results"] if user["role"] == "admin" else ["Available quizzes", "My results"]
    nav_col, out_col = st.columns([5, 1])
    with nav_col:
        page = st.radio("Navigation", options, horizontal=True, label_visibility="collapsed", key="admin_page" if user["role"] == "admin" else "student_page")
    with out_col:
        if st.button("Sign out", use_container_width=True):
            logout()
    if user["role"] == "admin":
        render_quiz_studio() if page == "Quiz studio" else render_class_results()
    else:
        render_student()

if __name__ == "__main__":
    main()
















