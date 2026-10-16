import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"

SYSTEM_PROMPT = (
    "You are Lumo, an expert and friendly study assistant. "
    "Explain concepts clearly with real-world examples. "
    "Keep answers focused: start with a short definition, then explain step by step, "
    "use simple markdown (short headings, bullet points, bold key terms), "
    "and end with one quick question to check understanding. "
    "Never generate quizzes here; tell the student to use the Quiz tab instead."
)


def stream_study_chat(prompt: str, history: list):
    """Streams a response for the chat UI, locked to study explanations."""
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)

    # Convert Streamlit history to Gemini format
    formatted_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        formatted_history.append({"role": role, "parts": [msg["content"]]})

    for attempt in range(3):
        started = False
        try:
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    started = True
                    yield chunk.text
            return
        except Exception:
            # If text was already shown, don't retry (it would repeat the answer)
            if started:
                yield "\n\n_(Connection interrupted. Please ask again to continue.)_"
                return
            if attempt == 2:
                yield "I am currently overloaded by API limits. Please try again in a few seconds."
                return
            time.sleep(3)
