import sqlite3
from datetime import datetime, timedelta
from core.memory import DB_PATH
from config import RATE_LIMIT

def is_rate_limited(user_id: int) -> bool:
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT count, window_start FROM rate_limit WHERE user_id=?",
            (user_id,)).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO rate_limit (user_id, count) VALUES (?, 1)", (user_id,))
            conn.commit()
            return False
        count, ws = row
        ws_dt = datetime.fromisoformat(ws)
        if ws_dt < window_start:
            conn.execute(
                "UPDATE rate_limit SET count=1, window_start=? WHERE user_id=?",
                (now.isoformat(), user_id))
            conn.commit()
            return False
        if count >= RATE_LIMIT:
            return True
        conn.execute(
            "UPDATE rate_limit SET count=count+1 WHERE user_id=?", (user_id,))
        conn.commit()
        return False
