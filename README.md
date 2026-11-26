# Quizly | Classroom Quiz Platform

Quizly is a classroom quiz platform with separate student and teacher spaces. Students can discover published quizzes, take timed attempts, review feedback, and follow their progress. Teachers can build and publish assessments, review class performance, and download filtered reports.

## Run on Windows

1. Install Python 3.10 or newer and select **Add Python to PATH** during setup.
2. Double-click **`run.bat`** in this project folder. It opens the project’s fixed address, `http://localhost:8504`, and starts this folder’s `app.py` if needed.

To start it manually, open a terminal in this folder and run:

   ```text
   py -m pip install -r requirements.txt
   py -m streamlit run app.py --server.port 8504
   ```

## First-time setup and demo

- On the sign-in screen, choose **Admin Login** and create the first teacher account. Teacher setup is available only until the first teacher account is created.
- Create a student account with **Create student account**, or sign in to an existing student account.
- Start with seven published quizzes: Starter Quiz, Python Fundamentals, Web Development Foundations, Computer Science Essentials, Mathematics & Data Reasoning, General Science: Core Ideas, and Digital Citizenship & Cyber Safety.
- In **Quiz studio**, copy a sample as a draft, edit its details and questions, or create a new quiz from scratch. Publish it when it is ready; students then see it in **Available quizzes**.

## Features

- Separate student and teacher sign-in. Passwords are stored as salted PBKDF2 hashes.
- Student quiz discovery with topic filters, search, sorting, completion status, score summaries, and recent attempts.
- Seven ready-to-play quizzes across programming, web development, computer science, mathematics, science, and digital citizenship.
- Teacher quiz studio with ready-made quizzes, create-from-scratch forms, duplicate-as-draft, editable quiz details, question add/remove controls, timed quizzes, and publish controls.
- Timed attempts, question navigation, review marks, answer review, explanations, weighted scoring, and score history.
- Teacher reports with quiz and student filters, sortable attempts, per-attempt answer review, hardest-question accuracy insights, and filtered CSV export.
- Responsive interface with high-contrast buttons, clear feedback, and animated controls.

## Local data

The app keeps `accounts.json`, `quizzes.json`, and `quiz_results.json` beside `app.py`; keep these local files with the app to retain accounts, teacher edits, and scores. The ready-made quiz templates live in `quiz_library.json` and are imported once into local quiz data. This is a local classroom/demo app: its JSON files are stored on the machine running Streamlit, not in a shared cloud database. Treat the login as classroom-level access, not production-grade security.

