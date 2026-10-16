import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"
GENERATION_CONFIG = genai.types.GenerationConfig(max_output_tokens=1500)


def generate_quiz(topic: str, num_questions: int, difficulty: str) -> list[dict]:
    model = genai.GenerativeModel(MODEL_NAME, generation_config=GENERATION_CONFIG)
    prompt = f"""Create a {difficulty} {num_questions}-question multiple-choice quiz about "{topic}".
Respond ONLY with a JSON list in this exact format:
[
  {{
    "question": "text",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "explanation": "Why this is correct"
  }}
]"""
    for attempt in range(3):
        try:
            response = model.generate_content(prompt, request_options={"timeout": 30})
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception:
            if attempt == 2:
                return []
            time.sleep(3)


def grade_answers(questions: list[dict], user_answers: list[int]) -> dict:
    score = sum(1 for q, ans in zip(questions, user_answers) if ans == q["correct_index"])
    return {"score": score, "total": len(questions), "weak": score < (len(questions) * 0.6)}
