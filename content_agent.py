"""
CONTENT AGENT
Takes a module name and generates a plain-language explanation for it.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"

# Capped so the reply (which is only meant to be a few short paragraphs)
# doesn't run long and slow things down.
GENERATION_CONFIG = genai.types.GenerationConfig(max_output_tokens=500)


def explain_module(module_name: str, topic: str = "") -> str:
    """
    Returns a plain-language explanation (a few short paragraphs) for the
    given module name.
    """
    model = genai.GenerativeModel(MODEL_NAME, generation_config=GENERATION_CONFIG)
    prompt = f"""You are a friendly tutor explaining a topic to a college student
with no prior background. Explain "{module_name}" (part of the broader topic
"{topic}") in plain, simple language.
Rules:
- Use short paragraphs and simple examples
- No jargon without explaining it first
- Keep it under 250 words
- End with one short real-world example
"""
    response = model.generate_content(prompt)
    return response.text.strip()


if __name__ == "__main__":
    # Simple test when you run: python content_agent.py
    explanation = explain_module("Primary Keys and Foreign Keys", "DBMS Basics")
    print(explanation)
