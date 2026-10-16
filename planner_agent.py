import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"
GENERATION_CONFIG = genai.types.GenerationConfig(
    max_output_tokens=1500,
    response_mime_type="application/json",
)


def _extract_json_list(text: str):
    """Pull a JSON list out of the model reply, even if wrapped in extra text."""
    text = text.strip().replace("```json", "").replace("```", "").strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON list found")
    return json.loads(text[start:end + 1])


def create_study_plan(topic: str, weak_areas: list[str] = None) -> list[str]:
    model = genai.GenerativeModel(MODEL_NAME, generation_config=GENERATION_CONFIG)
    weak_note = f"Focus extra on: {', '.join(weak_areas)}." if weak_areas else ""
    prompt = (
        f'Break "{topic}" into 3-5 learning modules, easiest to hardest. {weak_note} '
        f'Respond ONLY with a JSON list of strings. Example: ["Mod 1", "Mod 2"]'
    )
    # Retry logic for Free API limits
    for attempt in range(3):
        try:
            response = model.generate_content(prompt, request_options={"timeout": 30})
            plan = _extract_json_list(response.text)
            plan = [str(item) for item in plan if str(item).strip()]
            if plan:
                return plan
        except Exception:
            pass
        if attempt < 2:
            time.sleep(3)  # Wait and retry if quota exceeded
    return ["Introduction to " + topic, "Core Concepts", "Advanced " + topic]
