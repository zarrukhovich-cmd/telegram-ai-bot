import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from core.gemini_client import describe_image
from core.memory import save_message, get_or_create_user

logger = logging.getLogger(__name__)

async def handle_image(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username)

    if not update.message or not update.message.photo:
        return

    try:
        await ctx.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING)
    except Exception as e:
        logger.error(f"Error sending chat action: {e}")

    # Берём фото наивысшего качества
    photo = update.message.photo[-1]
    photo_file = await ctx.bot.get_file(photo.file_id)
    photo_bytes = await photo_file.download_as_bytearray()

    caption = update.message.caption or "Опиши это изображение подробно на русском языке."

    description = describe_image(bytes(photo_bytes), caption)
    save_message(user.id, "user", f"[отправил изображение] {caption}")
    save_message(user.id, "assistant", description)

    await update.message.reply_text(description)
