import streamlit as st
import time
import os
import base64
from datetime import datetime
from database import (
    verify_user, create_user, get_chat_history, get_db,
    save_chat_message, log_study_time, save_quiz_score,
)
from styles import apply_lumo_styles, CARD_CSS
from content_agent import stream_study_chat
from quiz_agent import generate_quiz
from ui import card

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
        st.markdown(f"**Good afternoon, {st.session_state.username}**")
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.chat_id = None
            st.session_state.messages = []
            st.session_state.page = "Chat"
            st.rerun()
        st.markdown("---")

        # Navigation
        for p in ["Chat", "Quiz", "Books", "Music"]:
            if st.button(f"📘 {p}", use_container_width=True):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # PAGES
    if st.session_state.page == "Chat":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Study Chat")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Ask about your study material..."):
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
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("model"):
                    response_placeholder = st.empty()
                    full_resp = ""
                    for chunk in stream_study_chat(prompt, st.session_state.messages[:-1]):
                        full_resp += chunk
                        response_placeholder.markdown(full_resp + "▌")
                    response_placeholder.markdown(full_resp)
                st.session_state.messages.append({"role": "model", "content": full_resp})
                save_chat_message(st.session_state.chat_id, "model", full_resp)

        with col2:
            st.markdown("<div class='lumo-card'>", unsafe_allow_html=True)
            st.markdown("#### ⏱️ Timer")
            render_timer()
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                if st.button("25/5"):
                    st.session_state.update(time_left=25 * 60, timer_running=False)
            with t_col2:
                if st.button("Start" if not st.session_state.timer_running else "Pause"):
                    st.session_state.timer_running = not st.session_state.timer_running
            with t_col3:
                if st.button("Focus"):
                    st.session_state.update(focus_mode=True, timer_running=True)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Quiz":
        st.markdown("### 📝 Quiz Generator")
        topic = st.text_input("Topic to quiz on")
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

    elif st.session_state.page == "Books":
        st.markdown("### 📚 Library")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_file:
            path = os.path.join("uploads", uploaded_file.name)
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            get_db().execute(
                "INSERT INTO books (user_id, title, file_path, uploaded_at) VALUES (?, ?, ?, ?)",
                (st.session_state.user_id, uploaded_file.name, path, datetime.now()),
            ).connection.commit()
            st.success("Uploaded!")

        books = get_db().execute(
            "SELECT * FROM books WHERE user_id=?", (st.session_state.user_id,)
        ).fetchall()
        for b in books:
            if st.button(f"📖 Read {b['title']}"):
                with open(b['file_path'], "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" '
                    f'height="600px"></iframe>',
                    unsafe_allow_html=True,
                )

    elif st.session_state.page == "Music":
        st.markdown("### 🎧 Focus Music")
        st.markdown(
            "<div class='lumo-card'>⚠️ <b>Note:</b> Freefy.app uses security headers that "
            "block embedding. Click below to open safely.</div>",
            unsafe_allow_html=True,
        )
        st.link_button("Open Freefy Player in New Tab ↗", "https://freefy.app/", type="primary")
