import html as _html
import streamlit as st
import time
import os
from datetime import datetime

# --- ANTI-CRASH IMPORT BLOCK ---
from database import (
    verify_user, create_user, get_chat_history, get_db,
    save_chat_message, log_study_time, save_quiz_score, get_progress_stats,
)
try:
    from database import get_chat_messages
except ImportError:
    # If Streamlit's cache is stuck on the old database.py, do it manually here so it never crashes!
    def get_chat_messages(chat_id):
        conn = get_db()
        rows = conn.execute("SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,)).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

from styles import apply_lumo_styles, CARD_CSS
from content_agent import stream_study_chat
from quiz_agent import generate_quiz
from planner_agent import create_study_plan
from pdf_agent import (
    extract_pdf_text, summarize_pdf, answer_from_pdf, next_question, check_answer,
)
from ui import page_header, stat_card, empty_state, progress_bar

st.set_page_config(page_title="Lumo | Study OS", page_icon="🧠", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)
apply_lumo_styles()

def _set_width(px):
    st.markdown(f"<style>[data-testid='stMainBlockContainer'], .main .block-container {{ max-width: {px}px !important; margin: 0 auto !important; width: 100% !important; }}</style>", unsafe_allow_html=True)

PAGE_ORDER = ["Start", "Chat", "Plan", "Quiz", "PDF Tutor", "Progress", "Notes"]
NAV_ICONS = {
    "Start": ":material/home:", "Chat": ":material/chat:", "Plan": ":material/map:",
    "Quiz": ":material/quiz:", "PDF Tutor": ":material/description:",
    "Progress": ":material/bar_chart:", "Notes": ":material/sticky_note_2:",
}

if not os.path.exists("uploads"): os.makedirs("uploads")

if "user_id" not in st.session_state: st.session_state.user_id = None
if "username" not in st.session_state: st.session_state.username = None
if "page" not in st.session_state: st.session_state.page = PAGE_ORDER[0]
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "messages" not in st.session_state: st.session_state.messages = []
if "timer_running" not in st.session_state: st.session_state.timer_running = False
if "time_left" not in st.session_state: st.session_state.time_left = 30 * 60
if "timer_total" not in st.session_state: st.session_state.timer_total = 30
if "timer_unlimited" not in st.session_state: st.session_state.timer_unlimited = False
if "timer_elapsed" not in st.session_state: st.session_state.timer_elapsed = 0

if "pdf_key" not in st.session_state: st.session_state.pdf_key = None
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""
if "pdf_question" not in st.session_state: st.session_state.pdf_question = ""
if "pdf_feedback" not in st.session_state: st.session_state.pdf_feedback = ""
if "pdf_asked" not in st.session_state: st.session_state.pdf_asked = []

def _ok(msg): st.success(msg, icon=":material/check_circle:")
def _warn(msg): st.warning(msg, icon=":material/warning:")
def _err(msg): st.error(msg, icon=":material/error:")
def _pdf_failed(text): return (not text) or text.startswith("Sorry, I couldn't get a reply")

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
    shown = st.session_state.timer_elapsed if st.session_state.timer_unlimited else st.session_state.time_left
    hrs, rem = divmod(shown, 3600)
    mins, secs = divmod(rem, 60)
    text = f"{hrs}:{mins:02d}:{secs:02d}" if hrs else f"{mins:02d}:{secs:02d}"
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{text}</h1>", unsafe_allow_html=True)

def _set_timer(minutes):
    if minutes is None: st.session_state.update(timer_unlimited=True, timer_running=False, timer_elapsed=0, time_left=0, timer_total=0)
    else: st.session_state.update(timer_unlimited=False, timer_running=False, timer_elapsed=0, time_left=minutes*60, timer_total=minutes)

def _toggle_timer():
    if not st.session_state.timer_unlimited and st.session_state.time_left <= 0:
        st.session_state.update(time_left=30*60, timer_total=30, timer_elapsed=0)
    st.session_state.timer_running = not st.session_state.timer_running

def _finish_timer():
    minutes = st.session_state.timer_elapsed // 60
    if minutes > 0:
        log_study_time(st.session_state.user_id, minutes)
        st.toast(f"Saved {minutes} min of study time.")
    st.session_state.update(timer_running=False, timer_elapsed=0)
    if not st.session_state.timer_unlimited: st.session_state.time_left = st.session_state.timer_total * 60

def _go(page):
    st.session_state.page = page
    st.rerun()

def show_login():
    _set_width(460)
    st.markdown("<div style='text-align:center; margin-top:8vh; margin-bottom: 24px;'><h1 style='font-family: var(--lumo-font-head); font-size: 4rem; letter-spacing: -0.03em; background: linear-gradient(180deg, #ffffff 25%, #b9f5dc 100%); -webkit-background-clip: text; color: transparent;'>Lumo</h1><p style='color:var(--lumo-muted);'>Explains topics, builds plans, and quizzes you.</p></div>", unsafe_allow_html=True)
    with st.container(border=True):
        t1, t2 = st.tabs(["Log in", "Create account"])
        with t1:
            u_l = st.text_input("Username", key="l_u")
            p_l = st.text_input("Password", type="password", key="l_p")
            if st.button("Log in", type="primary", use_container_width=True):
                uid = verify_user(u_l, p_l)
                if uid: st.session_state.update(user_id=uid, username=u_l); st.rerun()
                else: _err("Wrong credentials.")
        with t2:
            u_r = st.text_input("New username", key="r_u")
            p_r = st.text_input("New password", type="password", key="r_p")
            if st.button("Create account", type="primary", use_container_width=True):
                if create_user(u_r, p_r): _ok("Account created. Please log in.")
                else: _err("Username taken.")

if not st.session_state.user_id: show_login()
else:
    with st.sidebar:
        st.markdown(f"**Welcome back, {st.session_state.username}**")
        if st.button("New chat", icon=":material/add:", type="primary", use_container_width=True):
            st.session_state.update(chat_id=None, messages=[], page="Chat")
            st.rerun()
        st.markdown("---")
        for p in PAGE_ORDER:
            if st.button(p, icon=NAV_ICONS[p], type="primary" if st.session_state.page == p else "secondary", use_container_width=True): _go(p)
        
        st.markdown("---")
        st.markdown("<span style='color:var(--lumo-muted); font-size:0.75rem; font-weight:600; text-transform:uppercase;'>Recent Chats</span>", unsafe_allow_html=True)
        for chat in get_chat_history(st.session_state.user_id):
            if st.button(chat["title"][:25] + "...", key=f"sh_{chat['id']}", use_container_width=True):
                st.session_state.chat_id = chat["id"]
                st.session_state.messages = get_chat_messages(chat["id"])
                st.session_state.page = "Chat"
                st.rerun()

        st.markdown("---")
        if st.button("Log out", icon=":material/logout:", use_container_width=True): st.session_state.clear(); st.rerun()

    st.markdown("<div class='mobile-nav-container'>", unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: 
        if st.button("💬\nChat", key="m_c"): _go("Chat")
    with m2: 
        if st.button("🗺️\nPlan", key="m_p"): _go("Plan")
    with m3: 
        if st.button("📝\nQuiz", key="m_q"): _go("Quiz")
    with m4: 
        if st.button("📄\nPDF", key="m_f"): _go("PDF Tutor")
    with m5: 
        if st.button("📊\nStats", key="m_s"): _go("Progress")
    st.markdown("</div>", unsafe_allow_html=True)

    with st.popover("Timer" + (" (running)" if st.session_state.timer_running else ""), icon=":material/timer:"):
        st.markdown("#### Study timer")
        render_timer()
        p1, p2, p3 = st.columns(3)
        with p1: st.button("30m", on_click=_set_timer, args=(30,), use_container_width=True)
        with p2: st.button("60m", on_click=_set_timer, args=(60,), use_container_width=True)
        with p3: st.button("Unlim", on_click=_set_timer, args=(None,), use_container_width=True)
        b1, b2 = st.columns(2)
        with b1: st.button("Pause" if st.session_state.timer_running else "Start", type="primary", on_click=_toggle_timer, use_container_width=True)
        with b2: st.button("Finish", icon=":material/check:", on_click=_finish_timer, use_container_width=True)

    _set_width(980 if st.session_state.page in ("Start", "Progress") else 760)

    if st.session_state.page == "Start":
        page_header(f"Welcome back, {st.session_state.username}", "Pick where to start.")
        s1, s2, s3 = st.columns(3)
        with s1:
            with st.container(border=True):
                st.markdown("#### Ask a question")
                st.caption("Get a step-by-step explanation of any topic.")
                if st.button("Open chat", type="primary", use_container_width=True): _go("Chat")
        with s2:
            with st.container(border=True):
                st.markdown("#### Make a plan")
                st.caption("Break a subject into short lessons, easiest first.")
                if st.button("Open plan", use_container_width=True): _go("Plan")
        with s3:
            with st.container(border=True):
                st.markdown("#### Study from a PDF")
                st.caption("Upload a typed PDF, then get questions or summaries.")
                if st.button("Open PDF Tutor", use_container_width=True): _go("PDF Tutor")
        
        stats = get_progress_stats(st.session_state.user_id)
        if stats["minutes"] or stats["quizzes"]:
            st.markdown("#### Your progress")
            t1, t2, t3 = st.columns(3)
            with t1: stat_card("Minutes studied", stats["minutes"])
            with t2: stat_card("Quizzes taken", stats["quizzes"])
            with t3: stat_card("Average score", f"{stats['avg']}%")

    elif st.session_state.page == "Chat":
        page_header("Study chat", "Ask anything about your study material")
        
        if st.session_state.messages:
            chat_text = "\n\n".join([f"{m['role'].upper()}:\n{m['content']}" for m in st.session_state.messages])
            st.download_button("📥 Download Chat Notes", data=chat_text, file_name="lumo_notes.txt", use_container_width=True)

        prompt = st.chat_input("Ask about your study material...")
        if not prompt and st.session_state.get("auto_prompt"):
            prompt = st.session_state.pop("auto_prompt")

        if not st.session_state.messages and not prompt:
            empty_state("💬", "Start a conversation", "Ask about any topic and I'll explain it step by step.")
            st_cols = st.columns(2)
            for i, q in enumerate(["Explain database normalization", "Explain recursion", "TCP vs UDP", "How photosynthesis works"]):
                with st_cols[i % 2]:
                    if st.button(q, use_container_width=True):
                        st.session_state.auto_prompt = q
                        st.rerun()
            
            chat_hist = get_chat_history(st.session_state.user_id)
            if chat_hist:
                st.markdown("<div style='margin-top: 3rem; margin-bottom: 1rem; text-align: center; color: var(--lumo-muted); font-weight: 600; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;'>Continue a previous chat</div>", unsafe_allow_html=True)
                for chat in chat_hist[:5]:
                    if st.button(f"🕒 {chat['title']}", key=f"mh_{chat['id']}", use_container_width=True):
                        st.session_state.chat_id = chat["id"]
                        st.session_state.messages = get_chat_messages(chat["id"])
                        st.session_state.page = "Chat"
                        st.rerun()

        if prompt:
            if not st.session_state.chat_id:
                c = get_db().cursor()
                c.execute("INSERT INTO chats (user_id, title, created_at) VALUES (?, ?, ?)", (st.session_state.user_id, prompt[:30], datetime.now()))
                get_db().commit()
                st.session_state.chat_id = c.lastrowid
            st.session_state.messages.append({"role": "user", "content": prompt})
            save_chat_message(st.session_state.chat_id, "user", prompt)

            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                ph = st.empty()
                resp = ""
                for chunk in stream_study_chat(prompt, st.session_state.messages[:-1]):
                    resp += chunk; ph.markdown(resp + "▌")
                ph.markdown(resp)
            st.session_state.messages.append({"role": "model", "content": resp})
            save_chat_message(st.session_state.chat_id, "model", resp)

        for msg in reversed(st.session_state.messages[:-2] if prompt else st.session_state.messages):
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    elif st.session_state.page == "Plan":
        page_header("Study plan", "Break any subject into bite-sized lessons")
        pc1, pc2 = st.columns(2)
        with pc1: topic = st.text_input("Subject", placeholder="e.g. DBMS", key="p_top")
        with pc2: weak = st.text_input("Weak areas (optional, comma-separated)", key="p_wk")
        
        if st.button("Create plan", type="primary"):
            if topic:
                with st.spinner("Building your plan..."):
                    wl = [w.strip() for w in weak.split(",") if w.strip()]
                    st.session_state.plan = create_study_plan(topic, wl or None)
                    st.session_state.plan_subject = topic
            else: _warn("Type a subject first.")

        if st.session_state.get("plan"):
            st.success(f"Plan ready for {st.session_state.plan_subject}")
            plan_text = "\n".join([f"{i+1}. {m}" for i, m in enumerate(st.session_state.plan)])
            st.download_button("📥 Download Plan (PDF/Text)", data=plan_text, file_name="study_plan.txt")
            
            done = 0
            for i, mod in enumerate(st.session_state.plan):
                with st.container(border=True):
                    if st.checkbox(f"{i + 1}. {mod}", key=f"c_{i}"): done += 1
                    lc1, lc2 = st.columns(2)
                    with lc1:
                        if st.button("Learn this", key=f"l_{i}", icon=":material/menu_book:", use_container_width=True):
                            st.session_state.auto_prompt = f"Explain this topic step by step: {mod}"; _go("Chat")
                    with lc2:
                        if st.button("Quiz me", key=f"q_{i}", icon=":material/quiz:", use_container_width=True):
                            st.session_state.quiz_topic_input = mod; _go("Quiz")
            progress_bar(f"{done} of {len(st.session_state.plan)} done", round(done*100/len(st.session_state.plan)))

    elif st.session_state.page == "Quiz":
        page_header("Quiz generator", "Test yourself on any topic")
        qc1, qc2 = st.columns([3, 1])
        with qc1: topic = st.text_input("Topic to quiz on", key="quiz_topic_input")
        with qc2: diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        
        if st.button("Generate quiz", type="primary"):
            if topic:
                with st.spinner("Generating..."):
                    st.session_state.current_quiz = generate_quiz(topic, 3, diff)
                    for k in [k for k in st.session_state if k.startswith("qz_")]: del st.session_state[k]
                    st.session_state.update(quiz_topic=topic, quiz_saved=False)
            else: _warn("Type a topic first.")

        if st.session_state.get("current_quiz"):
            quiz = st.session_state.current_quiz
            ans = []
            for i, q in enumerate(quiz):
                with st.container(border=True):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    a = st.radio("Ops", q['options'], key=f"qz_{i}", label_visibility="collapsed", index=None)
                    ans.append(q['options'].index(a) if a else -1)

            if st.button("Submit answers", type="primary", use_container_width=True):
                if -1 in ans: _warn("Answer all questions before submitting.")
                else:
                    correct = sum(1 for i, q in enumerate(quiz) if ans[i] == q['correct_index'])
                    progress_bar(f"Score: {correct} / {len(quiz)}", round(correct * 100 / len(quiz)))
                    
                    if correct == len(quiz):
                        st.balloons()
                        _ok("Perfect score! 100%")
                    elif correct / len(quiz) >= 0.6:
                        st.snow()
                        _ok("Great job! You passed.")
                    else:
                        _err("Keep studying! Review your weak areas in the chat.")
                        
                    for i, q in enumerate(quiz):
                        if ans[i] != q['correct_index']: _warn(f"Q{i+1}: {q['explanation']}")
                        
                    if not st.session_state.get("quiz_saved"):
                        save_quiz_score(st.session_state.user_id, st.session_state.get("quiz_topic", topic), correct, len(quiz))
                        st.session_state.quiz_saved = True

    elif st.session_state.page == "PDF Tutor":
        page_header("PDF tutor", "Upload a PDF, then learn from it")
        file = st.file_uploader("Upload a PDF (max 10MB)", type="pdf")
        if file and file.size > 10*1024*1024: _err("PDF too large."); file = None
        
        if file:
            fk = f"{file.name}-{file.size}"
            if st.session_state.pdf_key != fk:
                with st.spinner("Reading PDF..."): st.session_state.pdf_text = extract_pdf_text(file.getvalue())
                st.session_state.update(pdf_key=fk, pdf_name=file.name, pdf_summary="", pdf_question="", pdf_feedback="", pdf_asked=[], pdf_reply="")
        
        pt = st.session_state.pdf_text
        if not file: empty_state("📄", "No PDF yet", "Upload a PDF to start.")
        elif not pt: _err("Couldn't read text. Try a typed PDF.")
        else:
            _ok(f"{st.session_state.pdf_name} ready.")
            mode = st.radio("Action", ["Ask me questions", "Explain this", "Summary"], horizontal=True)
            
            if mode == "Ask me questions":
                if not st.session_state.pdf_question:
                    if st.button("Start", type="primary"):
                        with st.spinner("Thinking..."):
                            q = next_question(pt, st.session_state.pdf_asked)
                            if not _pdf_failed(q): st.session_state.update(pdf_question=q, pdf_feedback=""); st.session_state.pdf_asked.append(q); st.rerun()
                            else: _err("Service busy.")
                else:
                    st.markdown(f"**Q:** {st.session_state.pdf_question}")
                    my_a = st.text_area("Your answer")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Check answer", type="primary", use_container_width=True):
                            if my_a:
                                with st.spinner("Checking..."):
                                    fb = check_answer(pt, st.session_state.pdf_question, my_a)
                                    if not _pdf_failed(fb): st.session_state.pdf_feedback = fb
                                    else: _err("Service busy.")
                            else: _warn("Type an answer first.")
                    with c2:
                        if st.button("Next question", use_container_width=True):
                            with st.spinner("Thinking..."):
                                q = next_question(pt, st.session_state.pdf_asked)
                                if not _pdf_failed(q): st.session_state.update(pdf_question=q, pdf_feedback=""); st.session_state.pdf_asked.append(q); st.rerun()
                    if st.session_state.pdf_feedback: st.info(st.session_state.pdf_feedback)
            
            elif mode == "Explain this":
                ask = st.text_input("What do you want to know?")
                if st.button("Explain", type="primary"):
                    if ask:
                        with st.spinner("Reading..."):
                            rep = answer_from_pdf(pt, ask)
                            if not _pdf_failed(rep): st.session_state.pdf_reply = rep
                            else: _err("Service busy.")
                if st.session_state.pdf_reply: st.markdown(st.session_state.pdf_reply)
            
            else:
                if st.button("Summarize PDF", type="primary"):
                    with st.spinner("Summarizing..."):
                        summ = summarize_pdf(pt)
                        if not _pdf_failed(summ): st.session_state.pdf_summary = summ
                        else: _err("Service busy.")
                if st.session_state.pdf_summary: st.markdown(st.session_state.pdf_summary)

    elif st.session_state.page == "Progress":
        page_header("Progress", "Your study stats")
        s = get_progress_stats(st.session_state.user_id)
        if s["quizzes"]:
            avg = max(0, min(100, round(float(s["avg"] or 0))))
            st.markdown(f'<div class="lumo-ring-wrap"><div class="lumo-ring" style="--pct:{avg}"><div class="lumo-ring-inner"><span class="lumo-ring-num">{avg}%</span><span class="lumo-ring-label">average</span></div></div></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: stat_card("Minutes", s["minutes"])
        with c2: stat_card("Quizzes", s["quizzes"])
        with c3: stat_card("Avg Score", f"{s['avg']}%")

    elif st.session_state.page == "Notes":
        page_header("Quick notes", "Jot things down")
        conn = get_db()
        conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, body TEXT, created_at TEXT)")
        conn.commit()
        with st.form("nf", clear_on_submit=True):
            t = st.text_input("Title (optional)")
            b = st.text_area("Note")
            if st.form_submit_button("Save note", type="primary", use_container_width=True):
                if b:
                    conn.execute("INSERT INTO notes (user_id, title, body, created_at) VALUES (?,?,?,?)", (st.session_state.user_id, t or b[:30], b, datetime.now().strftime("%d %b %Y")))
                    conn.commit(); _ok("Saved.")
        for n in conn.execute("SELECT * FROM notes WHERE user_id=? ORDER BY id DESC", (st.session_state.user_id,)).fetchall():
            with st.expander(f"{n[2]} - {n[4]}"):
                st.markdown(n[3])
                if st.button("Delete", key=f"del_{n[0]}"): conn.execute("DELETE FROM notes WHERE id=?", (n[0],)); conn.commit(); st.rerun()
