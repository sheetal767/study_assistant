import io
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"
MAX_CHARS = 150000

CONFIG = genai.types.GenerationConfig(max_output_tokens=8192)

SYSTEM = (
    "You are a friendly study tutor. Use ONLY the PDF text provided. "
    "If the answer is not in the PDF, say so clearly. Keep answers short "
    "and clear, with simple examples when helpful."
)


def extract_pdf_text(file_bytes: bytes) -> str:
    """Return the text of a PDF, or an empty string if none can be read."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            reader.decrypt("")
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages).strip()
        return text[:MAX_CHARS]
    except Exception as e:
        print(f"[pdf] extract failed: {type(e).__name__}: {e}")
        return ""


def _ask(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=SYSTEM,
            generation_config=CONFIG,
        )
        response = model.generate_content(prompt, request_options={"timeout": 90})
        return response.text.strip()
    except Exception as e:
        print(f"[pdf] gemini failed: {type(e).__name__}: {e}")
        return "Sorry, I couldn't get a reply right now. Please try again."


def summarize_pdf(pdf_text: str) -> str:
    prompt = (
        f"PDF TEXT:\n{pdf_text}\n\n"
        "Give a short summary of this PDF: first one line on what it is about, "
        "then 5-8 key points as bullets."
    )
    return _ask(prompt)


def answer_from_pdf(pdf_text: str, question: str) -> str:
    prompt = (
        f"PDF TEXT:\n{pdf_text}\n\n"
        f"Student question: {question}\n\n"
        "Answer from the PDF only."
    )
    return _ask(prompt)


def next_question(pdf_text: str, asked: list) -> str:
    already = "\n".join(f"- {q}" for q in asked) if asked else "none"
    prompt = (
        f"PDF TEXT:\n{pdf_text}\n\n"
        f"Questions already asked:\n{already}\n\n"
        "Ask the student ONE new short question about a different part of "
        "this PDF. Return only the question, nothing else."
    )
    return _ask(prompt)


def check_answer(pdf_text: str, question: str, answer: str) -> str:
    prompt = (
        f"PDF TEXT:\n{pdf_text}\n\n"
        f"Question: {question}\n"
        f"Student answer: {answer}\n\n"
        "Say if the answer is correct, partly correct, or wrong. "
        "Then give the right answer from the PDF in 1-3 sentences."
    )
    return _ask(prompt)
