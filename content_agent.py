import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


def stream_study_chat(prompt: str, history: list):
    """Streams a response for the chat UI, locked to study explanations."""
    model = genai.GenerativeModel(MODEL_NAME)

    # Convert Streamlit history to Gemini format
    formatted_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        formatted_history.append({"role": role, "parts": [msg["content"]]})

    system_prompt = (
        "You are Lumo, an expert study assistant. Explain concepts clearly with "
        "real-world examples. Never generate quizzes here."
    )

    for attempt in range(3):
        try:
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(f"{system_prompt}\n\nStudent: {prompt}", stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            break
        except Exception:
            if attempt == 2:
                yield "I am currently overloaded by API limits. Please try again in a few seconds."
            time.sleep(3)
