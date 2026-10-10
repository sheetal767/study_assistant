"""
MAIN APP — StudyFlow AI
Wires the Planner, Content, and Quiz agents together into a Streamlit website.
Run with: streamlit run app.py

NOTE: This file only changes the frontend/presentation layer. The agent
imports, cached wrappers, session-state keys, and control flow are the same
as before — no agent logic, signatures, or return formats were touched.
"""
import streamlit as st
from planner_agent import create_study_plan, create_remedial_modules
from content_agent import explain_module
from quiz_agent import generate_quiz, grade_answers

st.set_page_config(page_title="StudyFlow AI", page_icon="🧠", layout="centered")

# ---------------------------------------------------------------------------
# Cached wrappers: if someone already asked about the same topic/module
# before, reuse that answer instantly instead of waiting on the AI again.
# This cache is shared across ALL visitors, not just one session.
# (Unchanged from before — same functions, same cache keys.)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def cached_study_plan(topic: str, weak_areas_tuple: tuple):
    weak_areas = list(weak_areas_tuple) if weak_areas_tuple else None
    return create_study_plan(topic, weak_areas=weak_areas)

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def cached_explain_module(module_name: str, topic: str):
    return explain_module(module_name, topic)

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def cached_generate_quiz(module_name: str):
    return generate_quiz(module_name)

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def cached_remedial_modules(topic: str, weak_areas_tuple: tuple):
    return create_remedial_modules(topic, list(weak_areas_tuple))

import time

# ---- Persistent stats + dark mode (NOT cleared when starting a new topic) ----
if "stats" not in st.session_state:
    st.session_state.stats = {"topics": 0, "quizzes": 0, "total_score": 0, "total_possible": 0}
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "session_start" not in st.session_state:
    st.session_state.session_start = time.time()
if "topic_history" not in st.session_state:
    st.session_state.topic_history = []  # [{topic, modules, score, total}, ...]

DARK = st.session_state.dark_mode

# ---------------------------------------------------------------------------
# Custom styling (switches based on dark mode) — StudyFlow AI visual refresh
# ---------------------------------------------------------------------------
if DARK:
    bg = "linear-gradient(180deg, #14121F 0%, #1A1730 100%)"
    card_bg = "#211D38"
    card_bg_soft = "#272141"
    text_main = "#EDEBFA"
    text_sub = "#9C97BE"
    card_border = "#322C52"
    input_bg = "#272141"
else:
    bg = "linear-gradient(180deg, #FAF9FF 0%, #ffffff 40%)"
    card_bg = "#FFFFFF"
    card_bg_soft = "#F7F5FF"
    text_main = "#1F1B3A"
    text_sub = "#726E94"
    card_border = "#ECE9FA"
    input_bg = "#F7F5FF"

ACCENT = "#6C5CE7"
ACCENT_SOFT = "#8E7CFF"
GREEN = "#1AA260"
ORANGE = "#E67E22"
PINK = "#E84393"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {bg}; }}
    .block-container {{ max-width: 820px; padding-top: 1.25rem; padding-bottom: 3rem; }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{ background: #19152E; }}
    section[data-testid="stSidebar"] * {{ color: #E8E6FA !important; }}
    .sidebar-brand {{ display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }}
    .sidebar-brand .logo-icon {{ font-size: 22px; }}
    .sidebar-logo {{ font-size: 19px; font-weight: 800; color: white !important; letter-spacing: -0.3px; }}
    .sidebar-sub {{ font-size: 12px; opacity: 0.6; margin-bottom: 20px; margin-left: 30px; }}
    div[data-testid="stSidebar"] div.stButton > button {{
        background: transparent; border: 1px solid rgba(255,255,255,0.10);
        text-align: left; width: 100%; margin-bottom: 6px; font-weight: 500;
        font-size: 14.5px; transition: all 0.2s ease; border-radius: 10px;
    }}
    div[data-testid="stSidebar"] div.stButton > button:hover {{
        background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.25);
        transform: translateX(2px);
    }}
    /* Active nav item uses the primary (filled) button style */
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT_SOFT} 100%);
        border: none; box-shadow: 0 4px 14px rgba(108,92,231,0.35);
    }}
    .stat-box {{
        background: rgba(255,255,255,0.06); border-radius: 12px; padding: 11px 13px;
        margin-bottom: 7px; font-size: 13px; border: 1px solid rgba(255,255,255,0.06);
    }}
    .sidebar-divider {{ border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 14px 0; }}

    /* ---------- Shared animation ---------- */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .hero, .card, .module-grid-card, .stat-card {{ animation: fadeInUp 0.4s ease; }}

    /* ---------- Hero header ---------- */
    .hero {{
        background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT_SOFT} 100%);
        border-radius: 20px; padding: 30px 32px; color: white;
        margin-bottom: 26px; box-shadow: 0 12px 30px rgba(108, 92, 231, 0.22);
    }}
    .hero-top {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
    .hero-icon {{ font-size: 30px; }}
    .hero h1 {{ font-size: 25px; margin: 0; color: white; font-weight: 800; letter-spacing: -0.3px; }}
    .hero p {{ margin: 0; opacity: 0.92; font-size: 14.5px; line-height: 1.5; }}

    /* ---------- Badges ---------- */
    .agent-badge {{
        display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 999px;
        font-size: 12.5px; font-weight: 700; margin-bottom: 14px; letter-spacing: 0.1px;
    }}
    .badge-planner {{ background: #E7E3FF; color: {ACCENT}; }}
    .badge-content {{ background: #DFF6E8; color: {GREEN}; }}
    .badge-quiz    {{ background: #FFE9D6; color: {ORANGE}; }}
    .badge-done    {{ background: #FFE3EE; color: {PINK}; }}
    .badge-progress{{ background: #E0F0FE; color: #2E86DE; }}

    /* ---------- Cards ---------- */
    .card {{
        background: {card_bg}; border-radius: 18px; padding: 26px 28px;
        box-shadow: 0 2px 10px rgba(20, 20, 43, 0.05);
        border: 1px solid {card_border}; margin-bottom: 20px;
    }}
    .module-title {{ font-size: 21px; font-weight: 800; color: {text_main}; margin-bottom: 4px; letter-spacing: -0.2px; }}
    .module-sub {{ color: {text_sub}; font-size: 13.5px; margin-bottom: 18px; }}
    .section-heading {{
        font-size: 13px; font-weight: 700; color: {text_sub}; text-transform: uppercase;
        letter-spacing: 0.6px; margin: 18px 0 10px 0; display: flex; align-items: center; gap: 6px;
    }}
    .lesson-body {{ color: {text_main}; font-size: 15.5px; line-height: 1.75; }}

    /* ---------- Module grid (My Plan page) ---------- */
    .module-grid-card {{
        background: {card_bg}; border: 1px solid {card_border}; border-radius: 14px;
        padding: 14px 16px; margin-bottom: 10px; display: flex; align-items: center; gap: 12px;
    }}
    .module-grid-card.is-current {{ border: 1.5px solid {ACCENT}; background: {card_bg_soft}; }}
    .module-status-icon {{ font-size: 20px; flex-shrink: 0; }}
    .module-grid-text {{ flex: 1; }}
    .module-grid-name {{ font-size: 14.5px; font-weight: 600; color: {text_main}; }}
    .module-grid-tag {{
        font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 999px;
        text-transform: uppercase; letter-spacing: 0.4px;
    }}
    .tag-done {{ background: #DFF6E8; color: {GREEN}; }}
    .tag-current {{ background: #E7E3FF; color: {ACCENT}; }}
    .tag-upcoming {{ background: {card_bg_soft}; color: {text_sub}; }}

    /* ---------- Stat cards (Progress page) ---------- */
    .stat-card {{
        background: {card_bg_soft}; border: 1px solid {card_border}; border-radius: 14px;
        padding: 16px; text-align: center;
    }}
    .stat-card .stat-icon {{ font-size: 20px; margin-bottom: 4px; }}
    .stat-card .stat-value {{ font-size: 22px; font-weight: 800; color: {text_main}; }}
    .stat-card .stat-label {{ font-size: 12px; color: {text_sub}; font-weight: 600; }}
    .weak-chip {{
        display: inline-block; background: #FFF0E5; color: {ORANGE}; font-size: 12.5px;
        font-weight: 600; padding: 5px 12px; border-radius: 999px; margin: 3px 4px 3px 0;
    }}

    /* ---------- Empty states ---------- */
    .empty-state {{ text-align: center; padding: 30px 10px; color: {text_sub}; }}
    .empty-state .empty-icon {{ font-size: 34px; margin-bottom: 8px; display: block; }}

    /* ---------- Buttons ---------- */
    div.stButton > button {{
        border-radius: 11px; font-weight: 600; border: none; padding: 0.6rem 1.3rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease; font-size: 14.5px;
    }}
    div.stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 4px 14px rgba(108,92,231,0.25); }}
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT_SOFT} 100%);
    }}

    /* ---------- Inputs ---------- */
    div[data-testid="stTextInput"] input {{
        background: {input_bg}; border-radius: 12px; border: 1.5px solid {card_border};
        padding: 12px 16px; font-size: 15px;
    }}
    div[data-testid="stTextInput"] input:focus {{ border-color: {ACCENT}; }}

    /* ---------- Progress bar + alerts ---------- */
    div[data-testid="stProgress"] > div > div > div {{ transition: width 0.6s ease; background: {ACCENT}; }}
    [data-testid="stMarkdownContainer"] p {{ color: {text_main}; }}
    div[data-testid="stAlert"] {{ border-radius: 12px; }}

    /* ---------- Module dot strip ---------- */
    .dot-strip {{ display: flex; gap: 6px; margin: 2px 0 20px 0; flex-wrap: wrap; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .dot-done {{ background: {GREEN}; }}
    .dot-current {{ background: {ACCENT}; box-shadow: 0 0 0 3px {card_bg_soft}; }}
    .dot-upcoming {{ background: {card_border}; }}

    /* ---------- Quiz review ---------- */
    .review-row {{
        border-radius: 12px; padding: 12px 14px; margin-bottom: 8px; font-size: 13.5px;
        border: 1px solid {card_border};
    }}
    .review-correct {{ background: #EAFBF1; color: #0E7A42; }}
    .review-wrong {{ background: #FFF1F0; color: #C0392B; }}

    /* ---------- History cards ---------- */
    .history-card {{
        background: {card_bg_soft}; border: 1px solid {card_border}; border-radius: 12px;
        padding: 12px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
    }}
    .history-topic {{ font-weight: 700; font-size: 14px; color: {text_main}; }}
    .history-score {{ font-size: 13px; font-weight: 700; color: {ACCENT}; }}

    /* ---------- Mobile tweaks ---------- */
    @media (max-width: 600px) {{
        .card {{ padding: 18px 18px; }}
        .hero {{ padding: 22px 20px; }}
        .hero h1 {{ font-size: 21px; }}
        .module-title {{ font-size: 18px; }}
    }}
</style>
""", unsafe_allow_html=True)

# ---- Session state setup (unchanged keys/logic) ----
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
    st.markdown(
        '<div class="sidebar-brand"><span class="logo-icon">🧠</span>'
        '<span class="sidebar-logo">StudyFlow AI</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-sub">Multi-agent study companion</div>', unsafe_allow_html=True)

    nav_items = [("🏠", "Study"), ("📋", "My Plan"), ("📊", "Progress")]
    for icon, label in nav_items:
        is_active = st.session_state.page == label
        if st.button(f"{icon}  {label}", use_container_width=True,
                     type="primary" if is_active else "secondary",
                     key=f"nav_{label}"):
            st.session_state.page = label
            st.rerun()

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    dark_label = "☀️  Light mode" if DARK else "🌙  Dark mode"
    if st.button(dark_label, use_container_width=True, key="nav_dark"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # ---- Persistent stats block (real data only — no invented numbers) ----
    s = st.session_state.stats
    avg = round(s["total_score"] / s["total_possible"] * 100) if s["total_possible"] else 0
    st.markdown(f'<div class="stat-box">📚 Topics studied: <b>{s["topics"]}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box">📝 Quizzes taken: <b>{s["quizzes"]}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box">🎯 Avg score: <b>{avg}%</b></div>', unsafe_allow_html=True)
    elapsed_min = int((time.time() - st.session_state.session_start) / 60)
    elapsed_label = f"{elapsed_min} min" if elapsed_min < 60 else f"{elapsed_min // 60}h {elapsed_min % 60}m"
    st.markdown(f'<div class="stat-box">⏱️ Time studying: <b>{elapsed_label}</b></div>', unsafe_allow_html=True)

    if st.session_state.plan:
        done = st.session_state.module_index
        total = len(st.session_state.plan)
        st.caption(f"Current topic: {st.session_state.get('topic', '—')}")
        st.progress(min(done / total, 1.0) if total else 0, text=f"{done}/{total} modules")

    if st.button("🔄  Start new topic", use_container_width=True, key="nav_reset"):
        for key in ["plan", "module_index", "weak_areas", "stage", "topic",
                    "current_quiz", "quiz_module", "page", "content_cache", "logged_to_history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ---------------------------------------------------------------------------
# Page: My Plan — module cards with current/completed/upcoming states
# ---------------------------------------------------------------------------
if st.session_state.page == "My Plan":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-planner">🧭 Planner Agent</span>', unsafe_allow_html=True)
    if not st.session_state.plan:
        st.markdown(
            '<div class="empty-state"><span class="empty-icon">📋</span>'
            'No study plan yet<br><span style="font-size:13px;">'
            'Go to <b>Study</b> and enter a topic to generate one.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f'<div class="module-title">Plan for: {st.session_state.topic}</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-sub">Your modules, in order</div>', unsafe_allow_html=True)
        for i, mod in enumerate(st.session_state.plan):
            if i < st.session_state.module_index:
                icon, tag_class, tag_text, card_class = "✅", "tag-done", "Done", ""
            elif i == st.session_state.module_index:
                icon, tag_class, tag_text, card_class = "👉", "tag-current", "Current", "is-current"
            else:
                icon, tag_class, tag_text, card_class = "⬜", "tag-upcoming", "Upcoming", ""
            st.markdown(f"""
            <div class="module-grid-card {card_class}">
                <span class="module-status-icon">{icon}</span>
                <div class="module-grid-text">
                    <div class="module-grid-name">{mod}</div>
                </div>
                <span class="module-grid-tag {tag_class}">{tag_text}</span>
            </div>
            """, unsafe_allow_html=True)

        plan_text = f"Study Plan: {st.session_state.topic}\n\n" + "\n".join(
            f"{i+1}. {mod}" for i, mod in enumerate(st.session_state.plan)
        )
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                "⬇️  Download plan as .txt",
                data=plan_text,
                file_name=f"{st.session_state.topic.replace(' ', '_')}_study_plan.txt",
                mime="text/plain",
                use_container_width=True,
            )
        # Full notes export — only offered once at least one lesson has been
        # generated. Pulls from content_cache (already-fetched explanations),
        # no new AI calls.
        cache = st.session_state.get("content_cache", {})
        if cache:
            notes_text = f"Study Notes: {st.session_state.topic}\n\n"
            for i, mod in enumerate(st.session_state.plan):
                if i in cache:
                    notes_text += f"{'=' * 50}\n{i + 1}. {mod}\n{'=' * 50}\n{cache[i]}\n\n"
            with dl_col2:
                st.download_button(
                    "⬇️  Download all notes so far",
                    data=notes_text,
                    file_name=f"{st.session_state.topic.replace(' ', '_')}_notes.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Topic history (real data — only topics actually completed) ----
    if st.session_state.topic_history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">📚 Topics you\'ve completed</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.topic_history):
            st.markdown(
                f'<div class="history-card"><span class="history-topic">{h["topic"]}</span>'
                f'<span class="history-score">{h["modules"]} modules</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page: Progress — real stats only, styled as stat cards
# ---------------------------------------------------------------------------
elif st.session_state.page == "Progress":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="agent-badge badge-progress">📊 Progress</span>', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Your progress so far</div>', unsafe_allow_html=True)
    st.markdown('<div class="module-sub">Based on your actual activity this session</div>', unsafe_allow_html=True)

    s = st.session_state.stats
    avg = round(s["total_score"] / s["total_possible"] * 100) if s["total_possible"] else 0
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-icon">📚</div>'
                     f'<div class="stat-value">{s["topics"]}</div>'
                     f'<div class="stat-label">Topics studied</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-icon">📝</div>'
                     f'<div class="stat-value">{s["quizzes"]}</div>'
                     f'<div class="stat-label">Quizzes taken</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-icon">🎯</div>'
                     f'<div class="stat-value">{avg}%</div>'
                     f'<div class="stat-label">Avg score</div></div>', unsafe_allow_html=True)

    if st.session_state.plan:
        total = len(st.session_state.plan)
        done = st.session_state.module_index
        st.markdown('<div class="section-heading">📈 Current topic</div>', unsafe_allow_html=True)
        st.progress(min(done / total, 1.0) if total else 0, text=f"{st.session_state.topic}: {done}/{total} modules done")
        if st.session_state.weak_areas:
            st.markdown('<div class="section-heading">🧩 Needed extra practice</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="weak-chip">{area}</span>' for area in set(st.session_state.weak_areas))
            st.markdown(chips, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty-state"><span class="empty-icon">📊</span>'
            'Start a topic to see live progress here.</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page: Study — the main agent flow (logic unchanged, presentation refreshed)
# ---------------------------------------------------------------------------
else:
    st.markdown("""
    <div class="hero">
        <div class="hero-top"><span class="hero-icon">🧠</span><h1>StudyFlow AI</h1></div>
        <p>Your AI study team — Planner, Content, and Quiz agents — working together to help you learn smarter.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.stage == "topic_input":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-planner">🧭 Planner Agent</span>', unsafe_allow_html=True)
        st.markdown('<div class="module-title">What do you want to study today?</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-sub">The Planner Agent will break it into bite-sized modules.</div>', unsafe_allow_html=True)
        topic = st.text_input("Topic", placeholder="e.g. DBMS Basics", label_visibility="collapsed")
        if st.button("✨ Create Study Plan →", type="primary") and topic.strip():
            try:
                with st.spinner("Planning your study path... (usually 10-15 sec)"):
                    st.session_state.topic = topic
                    st.session_state.plan = cached_study_plan(topic, tuple())
                    st.session_state.module_index = 0
                    st.session_state.stage = "content"
                    st.session_state.stats["topics"] += 1
                st.rerun()
            except Exception:
                st.error(
                    "⏱️ That took too long or the connection dropped. "
                    "This usually happens with a weak/unstable internet connection. "
                    "Please check your internet and try again."
                )
                st.button("🔄 Try again")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "content":
        modules = st.session_state.plan
        idx = st.session_state.module_index
        if idx >= len(modules):
            st.session_state.stage = "done"
            st.rerun()
        else:
            st.progress(idx / len(modules), text=f"Module {idx + 1} of {len(modules)}")
            dots = "".join(
                f'<span class="dot {"dot-done" if i < idx else "dot-current" if i == idx else "dot-upcoming"}"></span>'
                for i in range(len(modules))
            )
            st.markdown(f'<div class="dot-strip">{dots}</div>', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<span class="agent-badge badge-content">📖 Content Agent</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="module-title">{modules[idx]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="module-sub">Topic: {st.session_state.topic}</div>', unsafe_allow_html=True)
            if "content_cache" not in st.session_state:
                st.session_state.content_cache = {}
            if idx not in st.session_state.content_cache:
                try:
                    with st.spinner("Generating explanation... (usually 10-15 sec)"):
                        st.session_state.content_cache[idx] = cached_explain_module(modules[idx], st.session_state.topic)
                except Exception:
                    st.error(
                        "⏱️ That took too long or something went wrong getting the explanation. "
                        "Please check your internet and try again."
                    )
                    st.button("🔄 Try again", key="retry_content")
                    st.stop()
            word_count = len(st.session_state.content_cache[idx].split())
            read_min = max(1, round(word_count / 200))
            st.markdown(
                f'<div class="section-heading">📘 Lesson · {read_min} min read</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="lesson-body">{st.session_state.content_cache[idx]}</div>', unsafe_allow_html=True)
            st.write("")
            st.button("I'm ready for the quiz →", type="primary",
                       on_click=lambda: st.session_state.update(stage="quiz"))
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "quiz":
        idx = st.session_state.module_index
        module_name = st.session_state.plan[idx]
        if "current_quiz" not in st.session_state or st.session_state.get("quiz_module") != module_name:
            try:
                with st.spinner("Generating quiz... (usually 10-15 sec)"):
                    st.session_state.current_quiz = cached_generate_quiz(module_name)
                    st.session_state.quiz_module = module_name
            except Exception:
                st.error(
                    "⏱️ That took too long or something went wrong generating the quiz. "
                    "Please check your internet and try again."
                )
                st.button("🔄 Try again", key="retry_quiz")
                st.stop()
        if not st.session_state.current_quiz:
            st.error("⚠️ The quiz didn't generate properly. Please try again.")
            if st.button("🔄 Try again", key="retry_quiz_empty"):
                del st.session_state["current_quiz"]
                st.rerun()
            st.stop()
        quiz = st.session_state.current_quiz
        answers = []
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-quiz">📝 Quiz Agent</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="module-title">Quiz: {module_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-sub">Answer all questions, then submit.</div>', unsafe_allow_html=True)
        for i, q in enumerate(quiz):
            st.markdown(f'<div class="section-heading">Question {i + 1}</div>', unsafe_allow_html=True)
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
                with st.spinner("Adding extra practice modules... (usually 10-15 sec)"):
                    remaining = st.session_state.plan[idx + 1:]
                    new_modules = cached_remedial_modules(
                        st.session_state.topic, tuple(st.session_state.weak_areas)
                    )
                    st.session_state.plan = st.session_state.plan[: idx + 1] + new_modules + remaining
            else:
                score_col2.success("Nice work!")

            # Per-question review — built from data already in `quiz`/`answers`,
            # no agent changes or extra AI calls needed.
            st.markdown('<div class="section-heading">🔍 Review</div>', unsafe_allow_html=True)
            for i, q in enumerate(quiz):
                is_correct = answers[i] == q["correct_index"]
                row_class = "review-correct" if is_correct else "review-wrong"
                icon = "✅" if is_correct else "❌"
                detail = "" if is_correct else (
                    f"<br><b>Correct answer:</b> {q['options'][q['correct_index']]}"
                )
                st.markdown(
                    f'<div class="review-row {row_class}">{icon} <b>Q{i+1}.</b> {q["question"]}{detail}</div>',
                    unsafe_allow_html=True,
                )

            st.session_state.module_index += 1
            del st.session_state["current_quiz"]
            st.session_state.stage = "content"
            st.button("Continue →", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "done":
        st.balloons()
        if not st.session_state.get("logged_to_history"):
            s = st.session_state.stats
            st.session_state.topic_history.append({
                "topic": st.session_state.topic,
                "modules": len(st.session_state.plan),
            })
            st.session_state.logged_to_history = True
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-done">🎉 All done</span>', unsafe_allow_html=True)
        st.markdown('<div class="module-title">You\'ve completed the full study plan!</div>', unsafe_allow_html=True)
        if st.session_state.weak_areas:
            st.markdown('<div class="section-heading">🧩 Areas you needed extra practice on</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="weak-chip">{area}</span>' for area in set(st.session_state.weak_areas))
            st.markdown(chips, unsafe_allow_html=True)
        st.write("")
        if st.button("Start a new topic", type="primary"):
            for key in ["plan", "module_index", "weak_areas", "stage", "topic",
                        "current_quiz", "quiz_module", "page", "content_cache", "logged_to_history"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
