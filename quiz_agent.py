import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"
GENERATION_CONFIG = genai.types.GenerationConfig(
    max_output_tokens=4000,
    response_mime_type="application/json",
)


def _extract_json_list(text: str):
    """Pull a JSON list out of the model reply, even if wrapped in extra text."""
    text = text.strip().replace("```json", "").replace("```", "").strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON list found")
    return json.loads(text[start:end + 1])


def _clean_questions(raw) -> list[dict]:
    """Keep only well-formed questions."""
    good = []
    for q in raw if isinstance(raw, list) else []:
        try:
            options = [str(o) for o in q["options"]]
            idx = int(q["correct_index"])
            if len(options) >= 2 and 0 <= idx < len(options) and q["question"]:
                good.append({
                    "question": str(q["question"]),
                    "options": options,
                    "correct_index": idx,
                    "explanation": str(q.get("explanation", "")),
                })
        except (KeyError, TypeError, ValueError):
            continue
    return good


def generate_quiz(topic: str, num_questions: int, difficulty: str) -> list[dict]:
    model = genai.GenerativeModel(MODEL_NAME, generation_config=GENERATION_CONFIG)
    prompt = f"""Create a {difficulty} {num_questions}-question multiple-choice quiz about "{topic}".
Each question must have exactly 4 options.
"correct_index" is the 0-based position of the right option.
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
            questions = _clean_questions(_extract_json_list(response.text))
            if questions:
                return questions
        except Exception:
            pass
        if attempt < 2:
            time.sleep(2)
    return []


def grade_answers(questions: list[dict], user_answers: list[int]) -> dict:
    score = sum(1 for q, ans in zip(questions, user_answers) if ans == q["correct_index"])
    return {"score": score, "total": len(questions), "weak": score < (len(questions) * 0.6)}
