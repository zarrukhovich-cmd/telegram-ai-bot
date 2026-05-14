import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters
)
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers.command_handler import start, help_cmd, clear, status
from handlers.message_handler import handle_message
from handlers.admin_handler import ban_user, broadcast, stats
from handlers.voice_handler import handle_voice
from handlers.image_handler import handle_image
from core.memory import init_db
from core.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()
logger.info("Инициализация базы данных — OK")

app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Регистрируем обработчики
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_cmd))
bot_app.add_handler(CommandHandler("clear", clear))
bot_app.add_handler(CommandHandler("status", status))
bot_app.add_handler(CommandHandler("ban", ban_user))
bot_app.add_handler(CommandHandler("broadcast", broadcast))
bot_app.add_handler(CommandHandler("stats", stats))
bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))
bot_app.add_handler(MessageHandler(filters.PHOTO, handle_image))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Инициализация вебхука при импорте (для Gunicorn)
if WEBHOOK_URL and "onrender.com" in WEBHOOK_URL:
    async def setup_webhook():
        await bot_app.initialize()
        await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
        logger.info(f"Вебхук установлен: {WEBHOOK_URL}")
    
    import threading
    def run_setup():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(setup_webhook())
    
    threading.Thread(target=run_setup).start()

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running 🤖", 200

if __name__ == "__main__":
    if WEBHOOK_URL and "onrender.com" in WEBHOOK_URL:
        # Для локального тестирования режима вебхука
        app.run(host="0.0.0.0", port=PORT)
    else:
        # Режим Polling (для локального запуска)
        logger.info("Запуск в режиме POLLING (локально)...")
        bot_app.run_polling()
