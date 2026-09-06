# PROJECT STATUS — Multi-Agent AI Study Assistant
Last updated: Day 1 (setup)

## What this project is
Solo S.Y.B.Sc IT Sem III Field Project. A Streamlit website where a student
enters a study topic, and 3 AI agents collaborate:
- Planner Agent: breaks topic into modules
- Content Agent: explains each module in plain language
- Quiz Agent: quizzes on each module, loops back to Planner Agent to add
  practice modules if the student scores below 60%

Built using Python + Streamlit + Google Gemini API (free tier).
The user does NOT know how to code — all code must be written in full, with
plain-language explanations and exact terminal commands.

## Files that exist so far
- `planner_agent.py` — done, generates a JSON list of module names
- `content_agent.py` — done, generates a plain-language explanation per module
- `quiz_agent.py` — done, generates MCQs and grades them (weak = <60%)
- `app.py` — done, Streamlit app wiring all 3 agents with a feedback loop
- `requirements.txt` — done

## Current stage
Day 1 complete: all starter code written and syntax-checked. Agent logic
(JSON parsing, grading) tested with a mocked API response. NOT yet tested
against the real Gemini API or run as a live Streamlit app, since that needs
your own free API key.

## What needs to happen next
1. Install Python + VS Code
2. Get a free Gemini API key from aistudio.google.com
3. Create a `.env` file with `GEMINI_API_KEY=...` (copy `.env.example` and fill it in)
4. Run `pip install -r requirements.txt`
5. Test each agent file individually (`python planner_agent.py`, etc.)
6. Debug whatever errors come up — paste the exact error text into your AI chat
7. Once all 3 agents work standalone, run `streamlit run app.py` and test
   the full flow
8. Fix bugs, polish
9. Deploy on Streamlit Community Cloud (needs a free GitHub repo first)
10. Write the Project Report using the architecture description in the roadmap

## Known things to watch for
- The `google-generativeai` package used in this code is now deprecated by
  Google in favor of `google-genai`. It still works for now, but if you get
  install or import errors, ask your AI to help you switch to the new
  `google-genai` package (the code changes are small).
- The model name "gemini-2.0-flash" in the code may need to be swapped for
  whatever is current on aistudio.google.com — check there if API calls fail
  with a "model not found" error
- User has zero coding background — always give full code, not snippets to
  merge themselves
- User wants this same file updated after every session so they can switch
  to a different free AI (ChatGPT, Google Antigravity) without losing context
