import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from core.memory import save_message, get_history, get_or_create_user
from core.gemini_client import ask_gemini
from core.personality import get_system_prompt
from core.antispam import is_rate_limited
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not update.message.text:
        return
    text = update.message.text

    user_row = get_or_create_user(user.id, user.username)

    # Проверка бана
    if user_row and user_row[2] == 1:
        return

    # Проверка спама
    if is_rate_limited(user.id):
        await update.message.reply_text(
            "⏳ Ты пишешь слишком быстро. Подожди минуту.")
        return

    # Показываем "печатает..."
    await ctx.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING)

    history = get_history(user.id)
    system_prompt = get_system_prompt()

    save_message(user.id, "user", text)
    response = ask_gemini(system_prompt, history, text)
    save_message(user.id, "assistant", response)

    logger.info(f"User {user.id} (@{user.username}): {text[:60]}")
    await update.message.reply_text(response)
