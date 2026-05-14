import logging
import io
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from core.gemini_client import ask_gemini
from core.personality import get_system_prompt
from core.memory import save_message, get_history, get_or_create_user

logger = logging.getLogger(__name__)

async def handle_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username)

    if not update.message or not update.message.voice:
        return

    try:
        await ctx.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING)
    except Exception as e:
        logger.error(f"Error sending chat action: {e}")

    # Скачиваем голосовое
    voice_file = await ctx.bot.get_file(update.message.voice.file_id)
    voice_bytes = await voice_file.download_as_bytearray()

    # Gemini не поддерживает прямую транскрипцию голоса без дополнительных библиотек
    # Используем текстовую заглушку с просьбой написать текстом
    # Для полной транскрипции нужен SpeechRecognition + ffmpeg
    await update.message.reply_text(
        "🎙️ Голосовые сообщения пока в разработке. "
        "Напиши текстом — отвечу сразу."
    )
