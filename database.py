import sqlite3
import bcrypt
import os
from datetime import datetime, timedelta

DB_FILE = "lumo.db"


def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, created_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, chat_id INTEGER, role TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_sessions (id INTEGER PRIMARY KEY, user_id INTEGER, minutes INTEGER, created_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_scores (id INTEGER PRIMARY KEY, user_id INTEGER, topic TEXT, score INTEGER, total INTEGER, created_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, file_path TEXT, uploaded_at DATETIME)''')
    conn.commit()


def create_user(username, password):
    conn = get_db()
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None


def verify_user(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if row and bcrypt.checkpw(password.encode('utf-8'), row['password'].encode('utf-8')):
        return row['id']
    return None


def save_chat_message(chat_id, role, content):
    conn = get_db()
    conn.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role, content))
    conn.commit()


def get_chat_history(user_id):
    conn = get_db()
    return conn.execute(
        "SELECT * FROM chats WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
    ).fetchall()


def log_study_time(user_id, minutes):
    conn = get_db()
    conn.execute(
        "INSERT INTO study_sessions (user_id, minutes, created_at) VALUES (?, ?, ?)",
        (user_id, minutes, datetime.now()),
    )
    conn.commit()


def save_quiz_score(user_id, topic, score, total):
    conn = get_db()
    conn.execute(
        "INSERT INTO quiz_scores (user_id, topic, score, total, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, topic, score, total, datetime.now()),
    )
    conn.commit()


def get_progress_stats(user_id):
    conn = get_db()
    mins = conn.execute(
        "SELECT COALESCE(SUM(minutes), 0) AS m FROM study_sessions WHERE user_id = ?",
        (user_id,),
    ).fetchone()["m"]
    q = conn.execute(
        "SELECT COUNT(*) AS n, COALESCE(SUM(score), 0) AS s, "
        "COALESCE(SUM(total), 0) AS t FROM quiz_scores WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    avg = round(q["s"] * 100 / q["t"]) if q["t"] else 0
    recent = conn.execute(
        "SELECT topic, score, total FROM quiz_scores WHERE user_id = ? "
        "ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    ).fetchall()
    return {"minutes": mins, "quizzes": q["n"], "avg": avg, "recent": recent}


init_db()
