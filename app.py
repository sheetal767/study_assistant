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

st.set_page_config(page_title="Lumo | Study OS", page_icon="🧠", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)
apply_lumo_styles()

# Ensure uploads folder exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --- SESSION STATE INITIALIZATION ---
if "user_id" not in st.session_state: st.session_state.user_id = None
if "username" not in st.session_state: st.session_state.username = None
if "page" not in st.session_state: st.session_state.page = "Chat"
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "messages" not in st.session_state: st.session_state.messages = []
if "timer_running" not in st.session_state: st.session_state.timer_running = False
if "time_left" not in st.session_state: st.session_state.time_left = 25 * 60
if "focus_mode" not in st.session_state: st.session_state.focus_mode = False
if "pdf_key" not in st.session_state: st.session_state.pdf_key = None
if "pdf_name" not in st.session_state: st.session_state.pdf_name = ""
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""
if "pdf_summary" not in st.session_state: st.session_state.pdf_summary = ""
if "pdf_question" not in st.session_state: st.session_state.pdf_question = ""
if "pdf_feedback" not in st.session_state: st.session_state.pdf_feedback = ""
if "pdf_asked" not in st.session_state: st.session_state.pdf_asked = []
if "pdf_reply" not in st.session_state: st.session_state.pdf_reply = ""


# --- TIMER FRAGMENT (Runs without reloading whole page) ---
@st.fragment(run_every=1)
def render_timer():
    if st.session_state.timer_running and st.session_state.time_left > 0:
        st.session_state.time_left -= 1
        if st.session_state.time_left == 0:
            st.session_state.timer_running = False
            log_study_time(st.session_state.user_id, 25)  # simplified logging
            st.toast("Time's up! Take a break.", icon="🔔")
    mins, secs = divmod(st.session_state.time_left, 60)
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{mins:02d}:{secs:02d}</h1>",
                unsafe_allow_html=True)


# --- TIMER BUTTON CALLBACKS ---
def _set_timer(minutes):
    st.session_state.update(time_left=minutes * 60, timer_running=False)


def _toggle_timer():
    if st.session_state.time_left <= 0:
        st.session_state.time_left = 25 * 60
    st.session_state.timer_running = not st.session_state.timer_running


def _start_focus():
    if st.session_state.time_left <= 0:
        st.session_state.time_left = 25 * 60
    st.session_state.update(focus_mode=True, timer_running=True)


# --- LOGIN / SIGNUP PAGE ---
def show_login():
    st.markdown("<div style='max-width: 400px; margin: 10vh auto;' class='lumo-card'>",
                unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🧠 Lumo</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u_login = st.text_input("Username", key="login_u")
        p_login = st.text_input("Password", type="password", key="login_p")
        if st.button("Login", type="primary", use_container_width=True):
            uid = verify_user(u_login, p_login)
            if uid:
                st.session_state.user_id = uid
                st.session_state.username = u_login
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with tab2:
        u_reg = st.text_input("New Username", key="reg_u")
        p_reg = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Sign Up", type="primary", use_container_width=True):
            uid = create_user(u_reg, p_reg)
            if uid:
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")
    st.markdown("</div>", unsafe_allow_html=True)


# --- MAIN APP LAYOUT ---
if not st.session_state.user_id:
    show_login()
else:
    # FOCUS MODE WRAPPER
    if st.session_state.focus_mode:
        st.markdown(
            "<style>.block-container{max-width:100%!important; padding:0!important;} "
            "section[data-testid='stSidebar'] {display: none;}</style>",
            unsafe_allow_html=True,
        )
        st.button("Exit Focus Mode", on_click=lambda: st.session_state.update(focus_mode=False))
        render_timer()
        st.stop()

    # SIDEBAR
    with st.sidebar:
        st.markdown(f"**Welcome back, {st.session_state.username}** 👋")
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.chat_id = None
            st.session_state.messages = []
            st.session_state.page = "Chat"
            st.rerun()
        st.markdown("---")

        # Navigation (active page is highlighted)
        NAV = {
            "Chat": "💬", "Plan": "🗺️", "Quiz": "📝",
            "PDF Tutor": "📄", "Progress": "📊", "Notes": "🗒️",
        }
        for p, icon in NAV.items():
            is_active = st.session_state.page == p
            if st.button(
                f"{icon} {p}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"nav_{p}",
            ):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # FLOATING TIMER (top right pill, opens a popup panel on every page)
    timer_label = "⏱️ Timer ●" if st.session_state.timer_running else "⏱️ Timer"
    with st.popover(timer_label):
        st.markdown("#### ⏱️ Study Timer")
        render_timer()
        p1, p2, p3 = st.columns(3)
        with p1:
            st.button("25m", key="tm_25", on_click=_set_timer, args=(25,), use_container_width=True)
        with p2:
            st.button("15m", key="tm_15", on_click=_set_timer, args=(15,), use_container_width=True)
        with p3:
            st.button("5m", key="tm_5", on_click=_set_timer, args=(5,), use_container_width=True)
        b1, b2 = st.columns(2)
        with b1:
            st.button(
                "Pause" if st.session_state.timer_running else "Start",
                key="tm_toggle", type="primary",
                on_click=_toggle_timer, use_container_width=True,
            )
        with b2:
            st.button("🎯 Focus", key="tm_focus", on_click=_start_focus, use_container_width=True)

    # PAGES
    if st.session_state.page == "Chat":
        page_header("Study Chat", "Ask anything about your study material")
        history = list(st.session_state.messages)

        # Chat box sits right under the title (inside a container = not pinned to the bottom)
        input_box = st.container()
        with input_box:
            prompt = st.chat_input("Ask about your study material...")

        # A "Learn this" tap on the Plan page sends its question here
        if not prompt and st.session_state.get("auto_prompt"):
            prompt = st.session_state.pop("auto_prompt")

        if not history and not prompt:
            empty_state("💬", "Start a conversation",
                        "Ask about any topic above and I'll explain it step by step.")

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
                with st.chat_message("assistant", avatar="🧠"):
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
                    with st.chat_message("assistant", avatar="🧠"):
                        st.markdown(msg["content"])

    elif st.session_state.page == "Plan":
        page_header("🗺️ Study Plan", "Break any subject into bite-sized lessons")
        plan_topic = st.text_input("Subject", placeholder="e.g. DBMS", key="plan_topic_input")
        weak_text = st.text_input("Weak areas (optional, separated by commas)", key="plan_weak_input")
        if st.button("Create Plan", type="primary") and plan_topic:
            with st.spinner("Building your plan..."):
                weak_list = [w.strip() for w in weak_text.split(",") if w.strip()]
                st.session_state.plan = create_study_plan(plan_topic, weak_list or None)
                st.session_state.plan_subject = plan_topic

        if st.session_state.get("plan"):
            subject = st.session_state.get("plan_subject", "")
            st.markdown(f"#### Your plan for {subject}")
            done = 0
            for i, module in enumerate(st.session_state.plan):
                if st.checkbox(f"{i + 1}. {module}", key=f"plan_{subject}_{i}"):
                    done += 1
                lc1, lc2 = st.columns(2)
                with lc1:
                    if st.button("📖 Learn this", key=f"learn_{subject}_{i}",
                                 use_container_width=True):
                        st.session_state.auto_prompt = (
                            f"Explain this topic step by step: {module}"
                        )
                        st.session_state.page = "Chat"
                        st.rerun()
                with lc2:
                    if st.button("📝 Quiz me", key=f"quizme_{subject}_{i}",
                                 use_container_width=True):
                        st.session_state.quiz_topic_input = module
                        st.session_state.page = "Quiz"
                        st.rerun()
            total = len(st.session_state.plan)
            progress_bar(f"{done} of {total} modules done", round(done * 100 / total))
            st.caption("Tip: tap Learn this on a module, then Quiz me to test yourself.")
        else:
            empty_state("🗺️", "No plan yet", "Enter a subject above and tap Create Plan.")

    elif st.session_state.page == "Quiz":
        page_header("📝 Quiz Generator", "Test yourself on any topic")
        topic = st.text_input("Topic to quiz on", key="quiz_topic_input")
        diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        if st.button("Generate Quiz", type="primary") and topic:
            with st.spinner("Generating..."):
                st.session_state.current_quiz = generate_quiz(topic, 3, diff)
                st.session_state.quiz_topic = topic
            if not st.session_state.current_quiz:
                st.error("⚠️ The quiz didn't generate properly. Please try again.")

        if st.session_state.get("current_quiz"):
            answers = []
            for i, q in enumerate(st.session_state.current_quiz):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                ans = st.radio("Options", q['options'], key=f"q{i}", index=None,
                               label_visibility="collapsed")
                answers.append(q['options'].index(ans) if ans else -1)

            if st.button("Submit Answers"):
                correct_count = 0
                for i, q in enumerate(st.session_state.current_quiz):
                    if answers[i] == q['correct_index']:
                        st.success(f"Q{i+1}: Correct!")
                        correct_count += 1
                    else:
                        st.error(f"Q{i+1}: Wrong. {q['explanation']}")
                save_quiz_score(
                    st.session_state.user_id,
                    st.session_state.get("quiz_topic", topic),
                    correct_count,
                    len(st.session_state.current_quiz),
                )

    elif st.session_state.page == "PDF Tutor":
        page_header("📄 PDF Tutor", "Upload one PDF, then learn from it")
        uploaded_file = st.file_uploader("Upload a PDF (one at a time, max 10MB)", type="pdf")
        if uploaded_file and uploaded_file.size > 10 * 1024 * 1024:
            st.error("⚠️ This PDF is bigger than 10MB. Please upload a smaller one.")
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

        if not uploaded_file:
            empty_state("📄", "No PDF yet", "Upload a PDF above to start learning from it.")
        elif not pdf_text:
            st.error("⚠️ I couldn't read any text in this PDF. Scanned or photo PDFs "
                     "won't work. Try a typed PDF.")
        else:
            st.success(f"📄 {st.session_state.pdf_name} is ready")
            if len(pdf_text) >= 150000:
                st.warning("This PDF is very long, so I'm only using the first part of it.")

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
                        st.session_state.pdf_question = q
                        st.session_state.pdf_asked.append(q)
                        st.session_state.pdf_feedback = ""
                        st.rerun()
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
                                st.session_state.pdf_feedback = check_answer(
                                    pdf_text, st.session_state.pdf_question, my_answer
                                )
                        else:
                            st.warning("Type your answer first.")

                    if next_clicked:
                        with st.spinner("Thinking of a question..."):
                            q = next_question(pdf_text, st.session_state.pdf_asked)
                        st.session_state.pdf_question = q
                        st.session_state.pdf_asked.append(q)
                        st.session_state.pdf_feedback = ""
                        st.rerun()

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
                            st.session_state.pdf_reply = answer_from_pdf(pdf_text, ask_text)
                    else:
                        st.warning("Type what you want to know first.")
                if st.session_state.pdf_reply:
                    st.markdown(st.session_state.pdf_reply)

            else:
                if st.button("Summarize PDF", type="primary", use_container_width=True):
                    with st.spinner("Summarizing..."):
                        st.session_state.pdf_summary = summarize_pdf(pdf_text)
                if st.session_state.pdf_summary:
                    st.markdown(st.session_state.pdf_summary)

    elif st.session_state.page == "Progress":
        page_header("📊 Progress", "Your study stats at a glance")
        stats = get_progress_stats(st.session_state.user_id)
        c1, c2, c3 = st.columns(3)
        with c1:
            stat_card("Minutes studied", stats["minutes"], "⏱️")
        with c2:
            stat_card("Quizzes taken", stats["quizzes"], "📝")
        with c3:
            stat_card("Average score", f"{stats['avg']}%", "🎯")

        st.markdown("#### Recent quizzes")
        if stats["recent"]:
            for r in stats["recent"]:
                pct = round(r["score"] * 100 / r["total"]) if r["total"] else 0
                progress_bar(f"{r['topic']} ({r['score']}/{r['total']})", pct)
        else:
            empty_state("📝", "No quizzes yet", "Take one in the Quiz tab and your scores will show here.")

    elif st.session_state.page == "Notes":
        page_header("🗒️ Quick Notes", "Jot things down while you study")
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
                "💾 Save note", type="primary", use_container_width=True
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
                st.success("Saved!")
            else:
                st.warning("Write something first.")

        notes = notes_conn.execute(
            "SELECT id, title, body, created_at FROM notes WHERE user_id=? ORDER BY id DESC",
            (st.session_state.user_id,),
        ).fetchall()

        if not notes:
            empty_state("🗒️", "No notes yet", "Write your first note above and tap Save.")
        for n in notes:
            with st.expander(f"{n[1]}  ·  {n[3]}"):
                st.markdown(n[2])
                if st.button("🗑️ Delete", key=f"del_note_{n[0]}"):
                    notes_conn.execute("DELETE FROM notes WHERE id=?", (n[0],))
                    notes_conn.commit()
                    st.rerun()
