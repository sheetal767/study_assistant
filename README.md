# 🧠 StudyFlow AI: Multi-Agent Study Assistant

StudyFlow AI is an AI-powered study app that helps you learn any subject step by step using Google Gemini. It works like your own little study team: one part explains, one plans, one quizzes you, and one reads your PDFs.

**Live App:** [studyassistant-drpcf3l6c3q34ff9zjcgfk.streamlit.app](https://studyassistant-drpcf3l6c3q34ff9zjcgfk.streamlit.app/)

---

## What This App Does

- **Explains Topics Simply:** Ask anything in Chat and get a clear, step-by-step explanation.
- **Creates Study Plans:** Enter a subject (like "DBMS") and it splits it into bite-sized lessons. Add your weak areas and it focuses on those.
- **Tests Your Knowledge:** Makes short multiple-choice quizzes at Easy, Medium or Hard.
- **Learns From Your PDF:** Upload a typed PDF, then get questions one by one, an explanation of any part, or a summary.
- **Tracks Progress:** See your minutes studied, quizzes taken, average score and recent quizzes.
- **Quick Notes:** Jot things down while you study.
- **Study Timer:** Choose 30 minutes, 60 minutes or unlimited. Tap Finish to save your study time.
- **Your Own Account:** Log in so your chats, scores and notes stay yours.

---

## Built With

- Python
- Streamlit
- Google Gemini
- SQLite
- bcrypt
- pypdf

---

## Project Files

- `app.py`: the main app (pages, sidebar, timer)
- `ui.py`: small reusable pieces like headers and stat cards
- `styles.py`: all the CSS for the dark look
- `database.py`: users, chats, scores and study time
- `content_agent.py`: the chat tutor
- `quiz_agent.py`: quiz maker
- `planner_agent.py`: study plan maker
- `pdf_agent.py`: PDF reader and tutor
- `test_lumo.py`: tests
- `PROJECT_STATUS.md`: progress notes
