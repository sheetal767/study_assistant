"""
MAIN APP
Wires the Planner, Content, and Quiz agents together into a Streamlit website.
Run with: streamlit run app.py
"""
import streamlit as st
from planner_agent import create_study_plan
from content_agent import explain_module
from quiz_agent import generate_quiz, grade_answers

st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="centered")

# ---- Persistent stats + dark mode (NOT cleared when starting a new topic) ----
if "stats" not in st.session_state:
    st.session_state.stats = {"topics": 0, "quizzes": 0, "total_score": 0, "total_possible": 0}
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

DARK = st.session_state.dark_mode

# ---------------------------------------------------------------------------
# Custom styling (switches based on dark mode)
# ---------------------------------------------------------------------------
if DARK:
    bg = "linear-gradient(180deg, #14121F 0%, #1A1730 100%)"
    card_bg = "#211D38"
    text_main = "#EDEBFA"
    text_sub = "#9C97BE"
    card_border = "#2E2A4A"
else:
    bg = "linear-gradient(180deg, #f7f5ff 0%, #ffffff 35%)"
    card_bg = "white"
    text_main = "#1a1a2e"
    text_sub = "#8a8a9e"
    card_border = "#F0EEFB"

st.markdown(f"""
<style>
    .stApp {{ background: {bg}; }}
    .block-container {{ max-width: 780px; padding-top: 1.5rem; }}
    section[data-testid="stSidebar"] {{ background: #1E1B3A; }}
    section[data-testid="stSidebar"] * {{ color: #E8E6FA !important; }}
    .sidebar-logo {{ font-size: 20px; font-weight: 800; color: white !important; margin-bottom: 2px; }}
    .sidebar-sub {{ font-size: 12px; opacity: 0.7; margin-bottom: 18px; }}
    div[data-testid="stSidebar"] div.stButton > button {{
        background: transparent; border: 1px solid rgba(255,255,255,0.12);
        text-align: left; width: 100%; margin-bottom: 6px; font-weight: 500;
        transition: all 0.2s ease;
    }}
    div[data-testid="stSidebar"] div.stButton > button:hover {{
        background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.3);
        transform: translateX(2px);
    }}
    .stat-box {{
        background: rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 12px;
        margin-bottom: 6px; font-size: 13px;
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .hero, .card {{ animation: fadeInUp 0.45s ease; }}
    .hero {{
        background: linear-gradient(135deg, #6C5CE7 0%, #8E7CFF 100%);
        border-radius: 20px; padding: 28px 32px; color: white;
        margin-bottom: 28px; box-shadow: 0 10px 30px rgba(108, 92, 231, 0.25);
    }}
    .hero h1 {{ font-size: 26px; margin: 0 0 6px 0; color: white; }}
    .hero p {{ margin: 0; opacity: 0.9; font-size: 15px; }}
    .agent-badge {{
        display: inline-block; padding: 4px 14px; border-radius: 999px;
        font-size: 13px; font-weight: 600; margin-bottom: 14px;
    }}
    .badge-planner {{ background: #E7E3FF; color: #6C5CE7; }}
    .badge-content {{ background: #DFF6E8; color: #1AA260; }}
    .badge-quiz    {{ background: #FFE9D6; color: #E67E22; }}
    .badge-done    {{ background: #FFE3EE; color: #E84393; }}
    .card {{
        background: {card_bg}; border-radius: 16px; padding: 24px 26px;
        box-shadow: 0 2px 8px rgba(20, 20, 43, 0.06);
        border: 1px solid {card_border}; margin-bottom: 20px;
    }}
    .module-title {{ font-size: 20px; font-weight: 700; color: {text_main}; margin-bottom: 4px; }}
    .module-sub {{ color: {text_sub}; font-size: 13px; margin-bottom: 18px; }}
    .plan-row {{
        display: flex; align-items: center; gap: 10px;
        padding: 10px 0; border-bottom: 1px solid {card_border}; font-size: 15px; color: {text_main};
    }}
    div.stButton > button {{
        border-radius: 10px; font-weight: 600; border: none; padding: 0.55rem 1.2rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div.stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(108,92,231,0.25); }}
    div.stButton > button[kind="primary"] {{ background: #6C5CE7; }}
    div[data-testid="stProgress"] > div > div > div {{ transition: width 0.6s ease; }}
    [data-testid="stMarkdownContainer"] p {{ color: {text_main}; }}
</style>
""", unsafe_allow_html=True)

# ---- Session state setup ----
if "plan" not in st.session_state:
    st.session_state.plan = None
    st.session_state.module_index = 0
    st.session_state.weak_areas = []
    st.session_state.stage = "topic_input"
if "page" not in st.session_state:
    st.session_state.page = "Study"

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📚 MultiAgent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Study Assistant</div>', unsafe_allow_html=True)

    if st.button("🏠  Study", use_container_width=True):
        st.session_state.page = "Study"
        st.rerun()
    if st.button("📋  My Plan", use_container_width=True):
        st.session_state.page = "My Plan"
        st.rerun()
    if st.button("📊  Progress", use_container_width=True):
        st.session_state.page = "Progress"
        st.rerun()

    st.markdown("---")

    dark_label = "☀️  Light mode" if DARK else "🌙  Dark mode"
    if st.button(dark_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")

    # ---- Persistent stats block ----
    s = st.session_state.stats
    avg = round(s["total_score"] / s["total_possible"] * 100) if s["total_possible"] else 0
    st.markdown(f'<div class="stat-box">📚 Topics studied: <b>{s["topics"]}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box">📝 Quizzes taken: <b>{s["quizzes"]}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box">🎯 Avg score: <b>{avg}%</b></div>', unsafe_allow_html=True)

    if st.session_state.plan:
        done = st.session_state.module_index
        total = len(st.session_state.plan)
        st.caption(f"Current topic: {st.session_state.get('topic', '—')}")
        st.progress(min(done / total, 1.0) if total else 0, text=f"{done}/{total} modules")

    if st.button("🔄  Start new topic", use_container_width=True):
        for key in ["plan", "module_index", "weak_areas", "stage", "topic",
                    "current_quiz", "quiz_module", "page", "content_cache"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ---------------------------------------------------------------------------
# Page: My Plan
# ---------------------------------------------------------------------------
if st.session_state.page == "My Plan":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-planner">🧭 Planner Agent</span>', unsafe_allow_html=True)
    if not st.session_state.plan:
        st.markdown('<div class="module-title">No study plan yet</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-sub">Go to Study and enter a topic to generate one.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="module-title">Plan for: {st.session_state.topic}</div>', unsafe_allow_html=True)
        for i, mod in enumerate(st.session_state.plan):
            icon = "✅" if i < st.session_state.module_index else ("👉" if i == st.session_state.module_index else "⬜")
            st.markdown(f'<div class="plan-row">{icon} <span>{mod}</span></div>', unsafe_allow_html=True)

        plan_text = f"Study Plan: {st.session_state.topic}\n\n" + "\n".join(
            f"{i+1}. {mod}" for i, mod in enumerate(st.session_state.plan)
        )
        st.download_button(
            "⬇️  Download plan as .txt",
            data=plan_text,
            file_name=f"{st.session_state.topic.replace(' ', '_')}_study_plan.txt",
            mime="text/plain",
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page: Progress
# ---------------------------------------------------------------------------
elif st.session_state.page == "Progress":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-quiz">📊 Progress</span>', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Your progress so far</div>', unsafe_allow_html=True)
    s = st.session_state.stats
    avg = round(s["total_score"] / s["total_possible"] * 100) if s["total_possible"] else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Topics studied", s["topics"])
    c2.metric("Quizzes taken", s["quizzes"])
    c3.metric("Avg score", f"{avg}%")
    if st.session_state.plan:
        total = len(st.session_state.plan)
        done = st.session_state.module_index
        st.markdown(f'<div class="module-sub">Current topic: {done}/{total} modules done</div>', unsafe_allow_html=True)
        if st.session_state.weak_areas:
            st.markdown('<div class="module-sub">Modules that needed extra practice:</div>', unsafe_allow_html=True)
            for area in set(st.session_state.weak_areas):
                st.write(f"- {area}")
    else:
        st.markdown('<div class="module-sub">Start a topic to see live progress here.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page: Study — the main agent flow
# ---------------------------------------------------------------------------
else:
    st.markdown("""
    <div class="hero">
        <h1>📚 Multi-Agent AI Study Assistant</h1>
        <p>Your AI study team — Planner, Content, and Quiz agents — working together to help you learn smarter.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.stage == "topic_input":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-planner">🧭 Planner Agent</span>', unsafe_allow_html=True)
        st.markdown('<div class="module-title">What do you want to study today?</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-sub">The Planner Agent will break it into bite-sized modules.</div>', unsafe_allow_html=True)
        topic = st.text_input("Topic", placeholder="e.g. DBMS Basics", label_visibility="collapsed")
        if st.button("Start studying →", type="primary") and topic.strip():
            with st.spinner("Planning your study path..."):
                st.session_state.topic = topic
                st.session_state.plan = create_study_plan(topic)
                st.session_state.module_index = 0
                st.session_state.stage = "content"
                st.session_state.stats["topics"] += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "content":
        modules = st.session_state.plan
        idx = st.session_state.module_index
        if idx >= len(modules):
            st.session_state.stage = "done"
            st.rerun()
        else:
            st.progress(idx / len(modules), text=f"Module {idx + 1} of {len(modules)}")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<span class="agent-badge badge-content">📖 Content Agent</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="module-title">{modules[idx]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="module-sub">Topic: {st.session_state.topic}</div>', unsafe_allow_html=True)
            if "content_cache" not in st.session_state:
                st.session_state.content_cache = {}
            if idx not in st.session_state.content_cache:
                with st.spinner("Generating explanation..."):
                    st.session_state.content_cache[idx] = explain_module(modules[idx], st.session_state.topic)
            st.write(st.session_state.content_cache[idx])
            st.button("I'm ready for the quiz →", type="primary",
                       on_click=lambda: st.session_state.update(stage="quiz"))
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "quiz":
        idx = st.session_state.module_index
        module_name = st.session_state.plan[idx]
        if "current_quiz" not in st.session_state or st.session_state.get("quiz_module") != module_name:
            with st.spinner("Generating quiz..."):
                st.session_state.current_quiz = generate_quiz(module_name)
                st.session_state.quiz_module = module_name
        quiz = st.session_state.current_quiz
        answers = []
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-quiz">📝 Quiz Agent</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="module-title">Quiz: {module_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-sub">Answer all questions, then submit.</div>', unsafe_allow_html=True)
        for i, q in enumerate(quiz):
            answer = st.radio(q["question"], q["options"], key=f"q_{i}", index=None)
            answers.append(q["options"].index(answer) if answer else -1)
        if st.button("Submit Quiz", type="primary"):
            result = grade_answers(quiz, answers)
            st.session_state.stats["quizzes"] += 1
            st.session_state.stats["total_score"] += result["score"]
            st.session_state.stats["total_possible"] += result["total"]
            score_col1, score_col2 = st.columns(2)
            score_col1.metric("Score", f"{result['score']} / {result['total']}")
            if result["weak"]:
                score_col2.warning("Needs more practice")
                st.session_state.weak_areas.append(module_name)
                with st.spinner("Adjusting your study plan..."):
                    remaining = st.session_state.plan[idx + 1:]
                    new_modules = create_study_plan(
                        st.session_state.topic, weak_areas=st.session_state.weak_areas
                    )
                    st.session_state.plan = st.session_state.plan[: idx + 1] + new_modules + remaining
            else:
                score_col2.success("Nice work!")
            st.session_state.module_index += 1
            del st.session_state["current_quiz"]
            st.session_state.stage = "content"
            st.button("Continue →", type="primary", on_click=lambda: st.rerun())
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "done":
        st.balloons()
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-done">🎉 All done</span>', unsafe_allow_html=True)
        st.markdown('<div class="module-title">You\'ve completed the full study plan!</div>', unsafe_allow_html=True)
        if st.session_state.weak_areas:
            st.markdown('<div class="module-sub">Areas you needed extra practice on:</div>', unsafe_allow_html=True)
            for area in set(st.session_state.weak_areas):
                st.write(f"- {area}")
        if st.button("Start a new topic", type="primary"):
            for key in ["plan", "module_index", "weak_areas", "stage", "topic",
                        "current_quiz", "quiz_module", "page", "content_cache"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
