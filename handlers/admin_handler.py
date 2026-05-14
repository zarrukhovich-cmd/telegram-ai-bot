import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from core.memory import DB_PATH
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

def admin_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Нет доступа.")
            return
        return await func(update, ctx)
    return wrapper

@admin_only
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    with sqlite3.connect(DB_PATH) as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_msgs = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        top = conn.execute(
            "SELECT username, message_count FROM users ORDER BY message_count DESC LIMIT 5"
        ).fetchall()
    top_text = "\n".join([f"@{u or 'unknown'}: {c} сообщ." for u, c in top])
    await update.message.reply_text(
        f"📊 *Статистика бота*\n\n"
        f"Пользователей: {total_users}\n"
        f"Всего сообщений: {total_msgs}\n\n"
        f"*Топ-5 активных:*\n{top_text}",
        parse_mode="Markdown"
    )

@admin_only
async def ban_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Использование: /ban [user_id]")
        return
    target_id = int(ctx.args[0])
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (target_id,))
        conn.commit()
    await update.message.reply_text(f"✅ Пользователь {target_id} заблокирован.")

@admin_only
async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Использование: /broadcast [текст]")
        return
    text = " ".join(ctx.args)
    with sqlite3.connect(DB_PATH) as conn:
        users = conn.execute(
            "SELECT user_id FROM users WHERE is_banned=0").fetchall()
    sent, failed = 0, 0
    for (uid,) in users:
        try:
            await ctx.bot.send_message(chat_id=uid, text=text)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"📢 Отправлено: {sent}, не доставлено: {failed}")
