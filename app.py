import html as _html
import streamlit as st
import time
import os
from datetime import datetime
from database import (
    verify_user, create_user, get_chat_history, get_db,
    save_chat_message, log_study_time, save_quiz_score, get_progress_stats,
)
from styles import apply_lumo_styles, CARD_CSS
from content_agent import stream_study_chat
from quiz_agent import generate_quiz
from planner_agent import create_study_plan
from pdf_agent import (
    extract_pdf_text, summarize_pdf, answer_from_pdf, next_question, check_answer,
)
from ui import card, page_header, stat_card, empty_state, progress_bar

st.set_page_config(page_title="Lumo", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)
apply_lumo_styles()


# --- LAYOUT: keep content in a centred column instead of stretching edge to edge ---
def _set_width(px):
    """Centre the main content and cap its width (px)."""
    st.markdown(
        f"""
        <style>
        [data-testid="stMainBlockContainer"],
        .main .block-container,
        section.main > div.block-container {{
            max-width: {px}px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            width: 100% !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Set to False to land straight in Chat after login (no Start page).
SHOW_START_PAGE = True

PAGE_ORDER = (["Start"] if SHOW_START_PAGE else []) + [
    "Chat", "Plan", "Quiz", "PDF Tutor", "Progress", "Notes",
]
NAV_ICONS = {
    "Start": ":material/home:", "Chat": ":material/chat:", "Plan": ":material/map:",
    "Quiz": ":material/quiz:", "PDF Tutor": ":material/description:",
    "Progress": ":material/bar_chart:", "Notes": ":material/sticky_note_2:",
}

# Ensure uploads folder exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --- SESSION STATE INITIALIZATION ---
if "user_id" not in st.session_state: st.session_state.user_id = None
if "username" not in st.session_state: st.session_state.username = None
if "page" not in st.session_state: st.session_state.page = PAGE_ORDER[0]
if "last_page" not in st.session_state: st.session_state.last_page = PAGE_ORDER[0]
if "page_history" not in st.session_state: st.session_state.page_history = []
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "messages" not in st.session_state: st.session_state.messages = []
if "timer_running" not in st.session_state: st.session_state.timer_running = False
if "time_left" not in st.session_state: st.session_state.time_left = 30 * 60
if "timer_total" not in st.session_state: st.session_state.timer_total = 30
if "timer_unlimited" not in st.session_state: st.session_state.timer_unlimited = False
if "timer_elapsed" not in st.session_state: st.session_state.timer_elapsed = 0
if "pdf_key" not in st.session_state: st.session_state.pdf_key = None
if "pdf_name" not in st.session_state: st.session_state.pdf_name = ""
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""
if "pdf_summary" not in st.session_state: st.session_state.pdf_summary = ""
if "pdf_question" not in st.session_state: st.session_state.pdf_question = ""
if "pdf_feedback" not in st.session_state: st.session_state.pdf_feedback = ""
if "pdf_asked" not in st.session_state: st.session_state.pdf_asked = []
if "pdf_reply" not in st.session_state: st.session_state.pdf_reply = ""


# --- MESSAGE HELPERS (status = icon + words, never colour alone) ---
def _ok(msg):
    st.success(msg, icon=":material/check_circle:")


def _warn(msg):
    st.warning(msg, icon=":material/warning:")


def _err(msg):
    st.error(msg, icon=":material/error:")


# The PDF helper returns this sentence when Gemini fails (see pdf_agent._ask).
# Treat it as an error instead of showing it as a question or an answer.
PDF_FAIL_PREFIX = "Sorry, I couldn't get a reply right now"


def _pdf_failed(text):
    return (not text) or text.startswith(PDF_FAIL_PREFIX)


# The planner returns this exact list when it can't reach Gemini.
def _is_fallback_plan(topic, plan):
    return plan == [f"Introduction to {topic}", "Core Concepts", f"Advanced {topic}"]


# --- TIMER FRAGMENT (Runs without reloading whole page) ---
@st.fragment(run_every=1)
def render_timer():
    if st.session_state.timer_running:
        st.session_state.timer_elapsed += 1
        if not st.session_state.timer_unlimited:
            st.session_state.time_left -= 1
            if st.session_state.time_left <= 0:
                st.session_state.time_left = 0
                st.session_state.timer_running = False
                st.session_state.timer_elapsed = 0
                log_study_time(st.session_state.user_id, st.session_state.timer_total)
                st.toast("Time's up! Take a break.")

    if st.session_state.timer_unlimited:
        shown = st.session_state.timer_elapsed
    else:
        shown = st.session_state.time_left

    hrs, rem = divmod(shown, 3600)
    mins, secs = divmod(rem, 60)
    if hrs:
        text = f"{hrs}:{mins:02d}:{secs:02d}"
    else:
        text = f"{mins:02d}:{secs:02d}"
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{text}</h1>",
                unsafe_allow_html=True)


# --- TIMER BUTTON CALLBACKS ---
def _set_timer(minutes):
    """minutes = 30 or 60, or None for unlimited (counts up)."""
    if minutes is None:
        st.session_state.update(
            timer_unlimited=True, timer_running=False,
            timer_elapsed=0, time_left=0, timer_total=0,
        )
    else:
        st.session_state.update(
            timer_unlimited=False, timer_running=False,
            timer_elapsed=0, time_left=minutes * 60, timer_total=minutes,
        )


def _toggle_timer():
    if not st.session_state.timer_unlimited and st.session_state.time_left <= 0:
        st.session_state.time_left = 30 * 60
        st.session_state.timer_total = 30
        st.session_state.timer_elapsed = 0
    st.session_state.timer_running = not st.session_state.timer_running


def _finish_timer():
    """Save the minutes studied so far and reset the timer."""
    minutes = st.session_state.timer_elapsed // 60
    if minutes > 0:
        log_study_time(st.session_state.user_id, minutes)
        st.toast(f"Saved {minutes} min of study time.")
    else:
        st.toast("Under 1 minute, nothing saved.")
    st.session_state.timer_running = False
    st.session_state.timer_elapsed = 0
    if not st.session_state.timer_unlimited:
        st.session_state.time_left = st.session_state.timer_total * 60


def _go(page):
    st.session_state.page = page
    st.rerun()


# --- OPENING SCREEN: LOGIN / SIGN UP ---
def show_login():
    _set_width(460)
    st.markdown(
        """
        <div class="lumo-login-hero">
            <div role="heading" aria-level="1" class="lumo-hero-title">Lumo</div>
            <div class="lumo-card" style="padding:12px 16px">
                <p class="lumo-lede">Lumo explains topics, builds study plans, quizzes you,
                and answers questions from a PDF you upload.</p>
            </div>
            <div class="lumo-chips">
                <span class="lumo-chip"><i style="background:#4ade80"></i>Explanations</span>
                <span class="lumo-chip"><i style="background:#2dd4bf"></i>Study plans</span>
                <span class="lumo-chip"><i style="background:#818cf8"></i>Quizzes</span>
                <span class="lumo-chip"><i style="background:#a78bfa"></i>PDF tutor</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if True:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["Log in", "Create account"])
            with tab1:
                u_login = st.text_input("Username", key="login_u")
                p_login = st.text_input("Password", type="password", key="login_p")
                if st.button("Log in", type="primary", use_container_width=True):
                    if not u_login.strip() or not p_login:
                        _warn("Enter your username and password.")
                    else:
                        uid = verify_user(u_login, p_login)
                        if uid:
                            st.session_state.user_id = uid
                            st.session_state.username = u_login
                            st.rerun()
                        else:
                            _err("Wrong username or password.")
            with tab2:
                u_reg = st.text_input("New username", key="reg_u")
                p_reg = st.text_input("New password", type="password", key="reg_p")
                if st.button("Create account", type="primary", use_container_width=True):
                    if not u_reg.strip() or not p_reg:
                        _warn("Choose a username and a password.")
                    else:
                        uid = create_user(u_reg, p_reg)
                        if uid:
                            _ok("Account created. Please log in.")
                        else:
                            _err("That username is already taken.")


# --- MAIN APP LAYOUT ---
if not st.session_state.user_id:
    show_login()
else:
    if st.session_state.page not in PAGE_ORDER:
        st.session_state.page = PAGE_ORDER[0]

    # Remember where the user came from (powers the Back button)
    if st.session_state.page != st.session_state.last_page:
        st.session_state.page_history.append(st.session_state.last_page)
        st.session_state.page_history = st.session_state.page_history[-20:]
        st.session_state.last_page = st.session_state.page

    # SIDEBAR
    with st.sidebar:
        _uname = str(st.session_state.username)
        st.markdown(
            '<div class="lumo-brand"><span class="lumo-brand-mark"></span>'
            '<span class="lumo-brand-name">Lumo</span></div>'
            '<div class="lumo-user"><span class="lumo-avatar">'
            + _html.escape(_uname[:1].upper() or "?")
            + '</span><div class="lumo-user-text"><div class="lumo-user-hi">Welcome back</div>'
            '<div class="lumo-user-name">' + _html.escape(_uname) + '</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.session_state.page_history:
            if st.button("Back", icon=":material/arrow_back:", use_container_width=True,
                         key="nav_back"):
                prev = st.session_state.page_history.pop()
                if prev not in PAGE_ORDER:
                    prev = PAGE_ORDER[0]
                st.session_state.page = prev
                st.session_state.last_page = prev
                st.rerun()
        if st.button("New chat", icon=":material/add:", use_container_width=True):
            st.session_state.chat_id = None
            st.session_state.messages = []
            st.session_state.page = "Chat"
            st.rerun()
        st.markdown("---")

        # Navigation (active page is highlighted)
        for p in PAGE_ORDER:
            is_active = st.session_state.page == p
            if st.button(
                p,
                icon=NAV_ICONS[p],
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"nav_{p}",
            ):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")
        if st.button("Log out", icon=":material/logout:", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # FLOATING TIMER (top right pill, opens a popup panel on every page)
    timer_label = "Timer (running)" if st.session_state.timer_running else "Timer"
    with st.popover(timer_label, icon=":material/timer:"):
        st.markdown("#### Study timer")
        render_timer()
        p1, p2, p3 = st.columns(3)
        with p1:
            st.button("30m", key="tm_30", on_click=_set_timer, args=(30,), use_container_width=True)
        with p2:
            st.button("60m", key="tm_60", on_click=_set_timer, args=(60,), use_container_width=True)
        with p3:
            st.button("Unlimited", key="tm_inf", on_click=_set_timer, args=(None,),
                      use_container_width=True)
        b1, b2 = st.columns(2)
        with b1:
            st.button(
                "Pause" if st.session_state.timer_running else "Start",
                key="tm_toggle", type="primary",
                on_click=_toggle_timer, use_container_width=True,
            )
        with b2:
            st.button("Finish", key="tm_finish", icon=":material/check:",
                      on_click=_finish_timer, use_container_width=True)

    # PAGES (centred column; the two card-grid pages get a little more room)
    _set_width(980 if st.session_state.page in ("Start", "Progress") else 760)
    if st.session_state.page == "Start":
        page_header(f"Welcome back, {st.session_state.username}", "Pick where to start.")
        s1, s2, s3 = st.columns(3)
        with s1:
            with st.container(border=True):
                st.markdown("#### Ask a question")
                st.caption("Get a step-by-step explanation of any topic.")
                if st.button("Open chat", key="start_chat", type="primary",
                             use_container_width=True):
                    _go("Chat")
        with s2:
            with st.container(border=True):
                st.markdown("#### Make a plan")
                st.caption("Break a subject into short lessons, easiest first.")
                if st.button("Open plan", key="start_plan", use_container_width=True):
                    _go("Plan")
        with s3:
            with st.container(border=True):
                st.markdown("#### Study from a PDF")
                st.caption("Upload a typed PDF, then get questions, explanations or a summary.")
                if st.button("Open PDF Tutor", key="start_pdf", use_container_width=True):
                    _go("PDF Tutor")

        start_stats = get_progress_stats(st.session_state.user_id)
        if start_stats["minutes"] or start_stats["quizzes"]:
            st.markdown("#### Your progress")
            t1, t2, t3 = st.columns(3)
            with t1:
                stat_card("Minutes studied", start_stats["minutes"])
            with t2:
                stat_card("Quizzes taken", start_stats["quizzes"])
            with t3:
                stat_card("Average score", f"{start_stats['avg']}%")
            if start_stats["recent"]:
                latest = start_stats["recent"][0]
                latest_pct = round(latest["score"] * 100 / latest["total"]) if latest["total"] else 0
                progress_bar(
                    f"Latest quiz: {latest['topic']} ({latest['score']}/{latest['total']})",
                    latest_pct,
                )

    elif st.session_state.page == "Chat":
        page_header("Study chat", "Ask anything about your study material")
        history = list(st.session_state.messages)

        # Chat box sits right under the title (inside a container = not pinned to the bottom)
        input_box = st.container()
        with input_box:
            prompt = st.chat_input("Ask about your study material...")

        # A "Learn this" tap on the Plan page sends its question here
        if not prompt and st.session_state.get("auto_prompt"):
            prompt = st.session_state.pop("auto_prompt")

        if not history and not prompt:
            empty_state("", "Start a conversation",
                        "Ask about any topic above and I'll explain it step by step.")
            st.caption("Or tap a question to begin")
            starters = [
                "Explain database normalization step by step",
                "Explain recursion with a simple analogy",
                "What is the difference between TCP and UDP?",
                "Summarize how photosynthesis works",
            ]
            st_cols = st.columns(2)
            for i, q in enumerate(starters):
                with st_cols[i % 2]:
                    if st.button(q, key=f"starter_{i}", use_container_width=True):
                        st.session_state.auto_prompt = q
                        st.rerun()
        else:
            st.caption("Newest messages appear first.")

        # Newest exchange appears right under the chat box
        live = st.container()
        if prompt:
            # Save chat session to DB if new
            if not st.session_state.chat_id:
                conn = get_db()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO chats (user_id, title, created_at) VALUES (?, ?, ?)",
                    (st.session_state.user_id, prompt[:30], datetime.now()),
                )
                conn.commit()
                st.session_state.chat_id = c.lastrowid

            st.session_state.messages.append({"role": "user", "content": prompt})
            save_chat_message(st.session_state.chat_id, "user", prompt)

            with live:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    full_resp = ""
                    for chunk in stream_study_chat(prompt, history):
                        full_resp += chunk
                        response_placeholder.markdown(full_resp + "▌")
                    response_placeholder.markdown(full_resp)
            st.session_state.messages.append({"role": "model", "content": full_resp})
            save_chat_message(st.session_state.chat_id, "model", full_resp)

        # Older conversation, newest first
        pairs = [history[i:i + 2] for i in range(0, len(history), 2)]
        for pair in reversed(pairs):
            for msg in pair:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.markdown(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(msg["content"])

    elif st.session_state.page == "Plan":
        page_header("Study plan", "Break any subject into bite-sized lessons")
        pc1, pc2 = st.columns(2)
        with pc1:
            plan_topic = st.text_input("Subject", placeholder="e.g. DBMS", key="plan_topic_input")
        with pc2:
            weak_text = st.text_input("Weak areas (optional, separated by commas)",
                                      key="plan_weak_input")
        if st.button("Create plan", type="primary"):
            if not plan_topic.strip():
                _warn("Type a subject first.")
            else:
                with st.spinner("Building your plan..."):
                    weak_list = [w.strip() for w in weak_text.split(",") if w.strip()]
                    st.session_state.plan = create_study_plan(plan_topic, weak_list or None)
                    st.session_state.plan_subject = plan_topic
                    st.session_state.plan_is_fallback = _is_fallback_plan(
                        plan_topic, st.session_state.plan
                    )

        if st.session_state.get("plan"):
            subject = st.session_state.get("plan_subject", "")
            st.markdown(f"#### Your plan for {subject}")
            if st.session_state.get("plan_is_fallback"):
                _warn("I couldn't reach the AI, so this is only a basic starter plan. "
                      "Wait a moment and tap Create plan again for a detailed one.")
            done = 0
            for i, module in enumerate(st.session_state.plan):
                with st.container(border=True):
                    if st.checkbox(f"{i + 1}. {module}", key=f"plan_{subject}_{i}"):
                        done += 1
                    lc1, lc2 = st.columns(2)
                    with lc1:
                        if st.button("Learn this", key=f"learn_{subject}_{i}",
                                     icon=":material/menu_book:", use_container_width=True):
                            st.session_state.auto_prompt = (
                                f"Explain this topic step by step: {module}"
                            )
                            st.session_state.page = "Chat"
                            st.rerun()
                    with lc2:
                        if st.button("Quiz me", key=f"quizme_{subject}_{i}",
                                     icon=":material/quiz:", use_container_width=True):
                            st.session_state.quiz_topic_input = module
                            st.session_state.page = "Quiz"
                            st.rerun()
            total = len(st.session_state.plan)
            progress_bar(f"{done} of {total} modules done", round(done * 100 / total))
            st.caption("Tip: tap Learn this on a module, then Quiz me to test yourself.")
        else:
            empty_state("", "No plan yet", "Enter a subject above and tap Create plan.")

    elif st.session_state.page == "Quiz":
        page_header("Quiz generator", "Test yourself on any topic")
        qc1, qc2 = st.columns([3, 1])
        with qc1:
            topic = st.text_input("Topic to quiz on", key="quiz_topic_input")
        with qc2:
            diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        if st.button("Generate quiz", type="primary"):
            if not topic.strip():
                _warn("Type a topic first.")
            else:
                with st.spinner("Generating..."):
                    new_quiz = generate_quiz(topic, 3, diff)
                # Forget answers picked in the previous quiz so they can't leak into this one
                for stale in [k for k in st.session_state if k[:1] == "q" and k[1:].isdigit()]:
                    del st.session_state[stale]
                st.session_state.current_quiz = new_quiz
                st.session_state.quiz_topic = topic
                st.session_state.quiz_saved = False
                if not new_quiz:
                    _err("The quiz didn't generate properly. Please try again.")

        if st.session_state.get("current_quiz"):
            quiz = st.session_state.current_quiz
            answers = []
            for i, q in enumerate(quiz):
                with st.container(border=True):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    ans = st.radio("Options", q['options'], key=f"q{i}", index=None,
                                   label_visibility="collapsed")
                answers.append(q['options'].index(ans) if ans in q['options'] else -1)

            if st.button("Submit answers"):
                if -1 in answers:
                    _warn("Please answer every question before submitting.")
                else:
                    correct_count = 0
                    for i, q in enumerate(quiz):
                        if answers[i] == q['correct_index']:
                            _ok(f"Q{i+1}: Correct!")
                            correct_count += 1
                        else:
                            _err(f"Q{i+1}: Wrong. {q['explanation']}")
                    progress_bar(f"Score: {correct_count} of {len(quiz)}",
                                 round(correct_count * 100 / len(quiz)))
                    # Save the score once per quiz, not on every Submit click
                    if not st.session_state.get("quiz_saved"):
                        save_quiz_score(
                            st.session_state.user_id,
                            st.session_state.get("quiz_topic", topic),
                            correct_count,
                            len(quiz),
                        )
                        st.session_state.quiz_saved = True
                    else:
                        st.caption("Your score for this quiz was already saved.")

    elif st.session_state.page == "PDF Tutor":
        page_header("PDF tutor", "Upload one PDF, then learn from it")
        uploaded_file = st.file_uploader("Upload a PDF (one at a time, max 10MB)", type="pdf")
        if uploaded_file and uploaded_file.size > 10 * 1024 * 1024:
            _err("This PDF is bigger than 10MB. Please upload a smaller one.")
            uploaded_file = None

        if uploaded_file:
            file_key = f"{uploaded_file.name}-{uploaded_file.size}"
            if st.session_state.pdf_key != file_key:
                with st.spinner("Reading your PDF..."):
                    text = extract_pdf_text(uploaded_file.getvalue())
                st.session_state.pdf_key = file_key
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.pdf_text = text
                st.session_state.pdf_summary = ""
                st.session_state.pdf_question = ""
                st.session_state.pdf_feedback = ""
                st.session_state.pdf_asked = []
                st.session_state.pdf_reply = ""
        else:
            st.session_state.pdf_key = None
            st.session_state.pdf_name = ""
            st.session_state.pdf_text = ""

        pdf_text = st.session_state.pdf_text
        PDF_BUSY = "Couldn't get a reply right now. Please try again."

        if not uploaded_file:
            empty_state("", "No PDF yet", "Upload a PDF above to start learning from it.")
        elif not pdf_text:
            _err("I couldn't read any text in this PDF. Scanned or photo PDFs "
                 "won't work. Try a typed PDF.")
        else:
            _ok(f"{st.session_state.pdf_name} is ready")
            if len(pdf_text) >= 150000:
                _warn("This PDF is very long, so I'm only using the first part of it.")

            mode = st.radio(
                "What do you want to do?",
                ["Ask me questions", "Explain this", "Summary"],
                horizontal=True,
                key="pdf_mode",
            )

            if mode == "Ask me questions":
                if not st.session_state.pdf_question:
                    st.caption("I'll ask you one question at a time from your PDF.")
                    if st.button("Start", type="primary", use_container_width=True):
                        with st.spinner("Thinking of a question..."):
                            q = next_question(pdf_text, st.session_state.pdf_asked)
                        if not _pdf_failed(q):
                            st.session_state.pdf_question = q
                            st.session_state.pdf_asked.append(q)
                            st.session_state.pdf_feedback = ""
                            st.rerun()
                        else:
                            _err(PDF_BUSY)
                else:
                    n = len(st.session_state.pdf_asked)
                    st.markdown(f"**Question {n}:** {st.session_state.pdf_question}")
                    my_answer = st.text_area("Your answer", key=f"pdf_ans_{n}")
                    c1, c2 = st.columns(2)
                    with c1:
                        check_clicked = st.button(
                            "Check answer", type="primary", use_container_width=True
                        )
                    with c2:
                        next_clicked = st.button("Next question", use_container_width=True)

                    if check_clicked:
                        if my_answer.strip():
                            with st.spinner("Checking..."):
                                fb = check_answer(
                                    pdf_text, st.session_state.pdf_question, my_answer
                                )
                            if not _pdf_failed(fb):
                                st.session_state.pdf_feedback = fb
                            else:
                                _err(PDF_BUSY)
                        else:
                            _warn("Type your answer first.")

                    if next_clicked:
                        with st.spinner("Thinking of a question..."):
                            q = next_question(pdf_text, st.session_state.pdf_asked)
                        if not _pdf_failed(q):
                            st.session_state.pdf_question = q
                            st.session_state.pdf_asked.append(q)
                            st.session_state.pdf_feedback = ""
                            st.rerun()
                        else:
                            _err(PDF_BUSY)

                    if st.session_state.pdf_feedback:
                        st.markdown(st.session_state.pdf_feedback)

            elif mode == "Explain this":
                ask_text = st.text_input(
                    "What do you want to know from this PDF?",
                    placeholder="e.g. explain normalization",
                    key="pdf_ask_input",
                )
                if st.button("Explain", type="primary", use_container_width=True):
                    if ask_text.strip():
                        with st.spinner("Reading the PDF..."):
                            reply = answer_from_pdf(pdf_text, ask_text)
                        if not _pdf_failed(reply):
                            st.session_state.pdf_reply = reply
                        else:
                            _err(PDF_BUSY)
                    else:
                        _warn("Type what you want to know first.")
                if st.session_state.pdf_reply:
                    st.markdown(st.session_state.pdf_reply)

            else:
                if st.button("Summarize PDF", type="primary", use_container_width=True):
                    with st.spinner("Summarizing..."):
                        summary = summarize_pdf(pdf_text)
                    if not _pdf_failed(summary):
                        st.session_state.pdf_summary = summary
                    else:
                        _err(PDF_BUSY)
                if st.session_state.pdf_summary:
                    st.markdown(st.session_state.pdf_summary)

    elif st.session_state.page == "Progress":
        page_header("Progress", "Your study stats at a glance")
        stats = get_progress_stats(st.session_state.user_id)
        if stats["quizzes"]:
            try:
                avg_pct = max(0, min(100, round(float(stats["avg"] or 0))))
            except (TypeError, ValueError):
                avg_pct = 0
            if avg_pct >= 80:
                ring_title, ring_note = "Excellent work", "Your scores are strong. Try a harder difficulty next."
            elif avg_pct >= 60:
                ring_title, ring_note = "Solid progress", "A few more quizzes will lift your average."
            else:
                ring_title, ring_note = "Keep going", "Retake quizzes on your weak topics to build confidence."
            st.markdown(
                '<div class="lumo-ring-wrap">'
                f'<div class="lumo-ring" style="--pct:{avg_pct}"><div class="lumo-ring-inner">'
                f'<span class="lumo-ring-num">{avg_pct}%</span>'
                '<span class="lumo-ring-label">average score</span></div></div>'
                f'<div class="lumo-ring-side"><div class="lumo-ring-title">{ring_title}</div>'
                f'<p>{ring_note}</p></div></div>',
                unsafe_allow_html=True,
            )
        c1, c2, c3 = st.columns(3)
        with c1:
            stat_card("Minutes studied", stats["minutes"])
        with c2:
            stat_card("Quizzes taken", stats["quizzes"])
        with c3:
            stat_card("Average score", f"{stats['avg']}%")

        st.markdown("#### Recent quizzes")
        if stats["recent"]:
            for r in stats["recent"]:
                pct = round(r["score"] * 100 / r["total"]) if r["total"] else 0
                progress_bar(f"{r['topic']} ({r['score']}/{r['total']})", pct)
        else:
            empty_state("", "No quizzes yet", "Take one in the Quiz tab and your scores will show here.")

    elif st.session_state.page == "Notes":
        page_header("Quick notes", "Jot things down while you study")
        notes_conn = get_db()
        notes_conn.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, title TEXT, body TEXT, created_at TEXT)"
        )
        notes_conn.commit()

        with st.form("note_form", clear_on_submit=True):
            n_title = st.text_input("Title (optional)")
            n_body = st.text_area("Your note", height=150)
            saved = st.form_submit_button(
                "Save note", icon=":material/save:", type="primary", use_container_width=True
            )
        if saved:
            if n_body.strip():
                note_title = n_title.strip() or n_body.strip()[:30]
                notes_conn.execute(
                    "INSERT INTO notes (user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
                    (
                        st.session_state.user_id,
                        note_title,
                        n_body.strip(),
                        datetime.now().strftime("%d %b %Y, %H:%M"),
                    ),
                )
                notes_conn.commit()
                _ok("Note saved.")
            else:
                _warn("Write something first.")

        notes = notes_conn.execute(
            "SELECT id, title, body, created_at FROM notes WHERE user_id=? ORDER BY id DESC",
            (st.session_state.user_id,),
        ).fetchall()

        if not notes:
            empty_state("", "No notes yet", "Write your first note above and tap Save note.")
        for n in notes:
            with st.expander(f"{n[1]}  ·  {n[3]}"):
                st.markdown(n[2])
                if st.button("Delete", key=f"del_note_{n[0]}", icon=":material/delete:"):
                    notes_conn.execute("DELETE FROM notes WHERE id=?", (n[0],))
                    notes_conn.commit()
                    st.rerun()
