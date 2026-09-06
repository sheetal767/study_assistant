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


def create_study_plan(topic: str, weak_areas: list[str] = None) -> list[str]:
    """
    Returns a list of module names (strings) for the given topic.
    If weak_areas is given, adds extra modules focused on those.
    """
    model = genai.GenerativeModel(MODEL_NAME)
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
    response = model.generate_content(prompt)
    text = response.text.strip()
    # Clean up if the model wraps it in ```json fences
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        modules = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: if parsing fails, just split by lines
        modules = [line.strip("-• ") for line in text.split("\n") if line.strip()]
    return modules


if __name__ == "__main__":
    # Simple test when you run: python planner_agent.py
    test_topic = "DBMS Basics"
    plan = create_study_plan(test_topic)
    print(f"Study plan for '{test_topic}':")
    for i, module in enumerate(plan, 1):
        print(f"{i}. {module}")
