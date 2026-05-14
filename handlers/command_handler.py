import logging
from telegram import Update
from telegram.ext import ContextTypes
from core.memory import clear_history, get_or_create_user
from core.personality import get_system_prompt

logger = logging.getLogger(__name__)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username)
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я AI-ассистент на базе Gemini. Просто напиши мне что-нибудь.\n\n"
        "Команды:\n"
        "/help — справка\n"
        "/clear — очистить историю разговора\n"
        "/status — твоя статистика"
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка*\n\n"
        "/start — начать заново\n"
        "/clear — удалить историю разговора\n"
        "/status — статистика\n\n"
        "Просто пиши — я отвечу. Помню контекст последних 20 сообщений.\n"
        "Отправь фото — опишу. Голосовое — расшифрую.",
        parse_mode="Markdown"
    )

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    clear_history(user.id)
    await update.message.reply_text("🗑️ История разговора очищена. Начинаем заново.")

async def status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    import sqlite3
    from core.memory import DB_PATH
    user = update.effective_user
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT message_count, first_seen FROM users WHERE user_id=?",
            (user.id,)).fetchone()
    if row:
        await update.message.reply_text(
            f"📊 *Твоя статистика*\n\n"
            f"Сообщений отправлено: {row[0]}\n"
            f"Первый визит: {row[1][:10]}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Данных пока нет. Напиши что-нибудь сначала.")
