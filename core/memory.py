import sqlite3
import os
from config import MAX_HISTORY

DB_PATH = "data/bot.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_banned INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit (
                user_id INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 0,
                window_start DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
        conn.commit()

def save_message(user_id: int, role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content))
        conn.commit()

def get_history(user_id: int) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, MAX_HISTORY)).fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def clear_history(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM messages WHERE user_id=?", (user_id,))
        conn.commit()

def get_or_create_user(user_id: int, username: str = None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username))
        conn.execute(
            "UPDATE users SET last_seen=CURRENT_TIMESTAMP, message_count=message_count+1 WHERE user_id=?",
            (user_id,))
        conn.commit()
        return conn.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
