# Quizly — classroom quiz app

A polished, responsive Streamlit quiz application for students and teachers. It keeps the original JSON question format while adding optional topic, difficulty, explanation, and point fields.

## Run locally

1. Install Python 3.9 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the app: `streamlit run app.py`

On Windows, `run.bat` starts the app after dependencies are installed.

## Student features

- Choose a topic, difficulty, question count, shuffle mode, and optional timer.
- Move between questions, jump directly to a question, and mark items for review.
- Review unanswered questions before submitting.
- See weighted score, elapsed time, correct answers, explanations, and answer review.
- Retake a quiz without losing the saved class results.

## Teacher features

- Add, edit, search, filter, and delete questions.
- Organize questions by topic and difficulty and assign points.
- Import or export a JSON question bank.
- Review recent attempts and download a CSV report.

Question banks are stored in `quiz_data.json`; results are stored locally in `quiz_results.json`. Keep these files with `app.py`. This classroom starter stores results on the machine running Streamlit; it does not provide separate teacher login or multi-user cloud storage.

### Question format

```json
{
  "q": "What is 2 + 2?",
  "options": ["3", "4", "5"],
  "ans": "4",
  "category": "Math",
  "difficulty": "Easy",
  "points": 1,
  "explanation": "Two plus two equals four."
}
```
The original `q`, `options`, and `ans` fields are still supported. Optional fields receive sensible defaults.
