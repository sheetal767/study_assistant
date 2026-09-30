"""
PLANNER AGENT
Takes a topic (e.g. "DBMS Basics") and breaks it into 3-5 learning modules.
Can also be called again with "weak_areas" to adjust the plan.
"""
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# NOTE: if this model name errors out, check aistudio.google.com for the
# current available free model name and swap it in here.
MODEL_NAME = "gemini-3.6-flash"

# Keeping the response short (it's just a JSON list of module names) makes
# the AI reply faster, which matters most on mobile connections.
GENERATION_CONFIG = genai.types.GenerationConfig(max_output_tokens=600)


def create_study_plan(topic: str, weak_areas: list[str] = None) -> list[str]:
    """
    Returns a list of module names (strings) for the given topic.
    If weak_areas is given, adds extra modules focused on those.
    """
    model = genai.GenerativeModel(MODEL_NAME, generation_config=GENERATION_CONFIG)
    weak_note = ""
    if weak_areas:
        weak_note = (
            f"The student is weak in: {', '.join(weak_areas)}. "
            "Add 1-2 extra focused modules for these before moving on."
        )
    prompt = f"""You are an educational planning assistant.
Break the topic "{topic}" into 3 to 5 clear learning modules, ordered from
easiest to hardest. {weak_note}
Respond ONLY with a JSON list of module name strings, nothing else.
Example format: ["Module 1 name", "Module 2 name", "Module 3 name"]
"""
    response = model.generate_content(
        prompt,
        request_options={"timeout": 30},
    )
    text = response.text.strip()
    # Clean up if the model wraps it in ```json fences
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        modules = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: try to salvage a comma-separated list even from
        # truncated/broken JSON (e.g. "[\"A\", \"B\"" with no closing bracket),
        # instead of showing the raw broken text as a module name.
        cleaned = text.strip().lstrip("[").rstrip("]").rstrip(",")
        parts = [p.strip().strip('"').strip("'") for p in cleaned.split(",")]
        # A real module name should have at least a few letters in it —
        # this rejects junk like "]", "*", or other stray fragments.
        modules = [
            p for p in parts
            if p and not p.startswith("{") and len(p) < 100
            and sum(c.isalpha() for c in p) >= 3
        ]
        if not modules:
            # Nothing usable was salvaged — raise so the caller's
            # try/except shows a proper "try again" message instead of
            # silently continuing with a broken/empty plan.
            raise ValueError("Planner Agent returned an unusable response")
    return modules


def create_remedial_modules(topic: str, weak_areas: list[str]) -> list[str]:
    """
    Returns just 1-2 SHORT extra practice module names focused on the
    student's weak areas — NOT a full new curriculum. Use this (not
    create_study_plan) when a student fails a quiz and needs targeted
    extra practice before moving on.
    """
    model = genai.GenerativeModel(MODEL_NAME, generation_config=GENERATION_CONFIG)
    prompt = f"""A student studying "{topic}" is struggling with: {', '.join(weak_areas)}.
Suggest 1 to 2 SHORT extra practice module names to help specifically with
this weak area. Do NOT design a full course — just short, focused revision
modules.
Respond ONLY with a JSON list of module name strings.
Example: ["Extra Practice: Primary Keys"]
"""
    response = model.generate_content(prompt, request_options={"timeout": 30})
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        modules = json.loads(text)
        if not isinstance(modules, list) or not modules:
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        # Safe fallback: one generic extra-practice module, never the whole plan
        modules = [f"Extra Practice: {weak_areas[-1]}"]
    return modules


if __name__ == "__main__":
    # Simple test when you run: python planner_agent.py
    test_topic = "DBMS Basics"
    plan = create_study_plan(test_topic)
    print(f"Study plan for '{test_topic}':")
    for i, module in enumerate(plan, 1):
        print(f"{i}. {module}")
