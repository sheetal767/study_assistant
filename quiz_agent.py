"""
QUIZ AGENT
Generates quiz questions for a module, and grades the student's answers.
"""
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


def generate_quiz(module_name: str, num_questions: int = 3) -> list[dict]:
    """
    Returns a list of dicts, each like:
    {"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}
    """
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""Create {num_questions} multiple-choice quiz questions about
"{module_name}" for a college student.
Respond ONLY with a JSON list, no other text, in this exact format:
[
  {{
    "question": "question text here",
    "options": ["option A", "option B", "option C", "option D"],
    "correct_index": 0
  }}
]
correct_index is the 0-based index of the correct option in the options list.
"""
    response = model.generate_content(prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        questions = json.loads(text)
    except json.JSONDecodeError:
        questions = []
    return questions


def grade_answers(questions: list[dict], user_answers: list[int]) -> dict:
    """
    Compares user_answers (list of chosen option indices) against the correct
    answers. Returns a dict: {"score": int, "total": int, "weak": bool}
    """
    score = 0
    for q, user_ans in zip(questions, user_answers):
        if user_ans == q["correct_index"]:
            score += 1
    total = len(questions)
    weak = score < (total * 0.6)  # below 60% counts as "weak" on this module
    return {"score": score, "total": total, "weak": weak}


if __name__ == "__main__":
    # Simple test when you run: python quiz_agent.py
    quiz = generate_quiz("Primary Keys and Foreign Keys")
    for i, q in enumerate(quiz, 1):
        print(f"Q{i}: {q['question']}")
        for j, opt in enumerate(q["options"]):
            print(f"   {j}. {opt}")
        print(f"   (correct: {q['correct_index']})\n")
