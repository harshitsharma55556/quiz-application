# Quizly — classroom quiz app

A Streamlit classroom quiz app with separate student and teacher accounts. Students can see only quizzes published by a teacher. Teachers create quizzes, add questions, and publish or unpublish them from the studio.

## Run on Windows

1. Install Python 3.10 or newer and select **Add Python to PATH** during setup.
2. Open this folder in File Explorer, click the address bar, type `cmd`, and press Enter.
3. Run:

   ```text
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

You can also double-click `run.bat` after installing Python and the dependencies.

## First-time setup

- On the sign-in screen, open **Admin / teacher** and create the first teacher account. The setup form closes after the first admin account exists.
- Students can create their own accounts from **Create student account**.
- The existing questions in `quiz_data.json` become a published **Starter Quiz**, and a 10-question **Python Fundamentals** quiz is included for students.
- In **Quiz studio**, create a draft, add questions, and publish it. Students then see it under **Available quizzes**.

## Features

- Separate student and teacher sign-in. Passwords are stored as salted PBKDF2 hashes.
- Students see published quizzes and their own attempts.
- Teachers can create quizzes, add questions, set a timer and shuffle order, then publish or unpublish them.
- Timed attempts, question navigation, review marks, answer review, explanations, weighted scoring, and score history.
- Teacher class results with CSV download.
- Responsive interface using Manrope and DM Sans with system-font fallbacks.

## Local data

The app creates `accounts.json`, `quizzes.json`, and `quiz_results.json` beside `app.py`. Keep those files with the app. This is a local classroom/demo app: its JSON files are stored on the machine running Streamlit, not in a shared cloud database. Do not expose it as a public website and treat the local login as classroom-level access, not production-grade security.

