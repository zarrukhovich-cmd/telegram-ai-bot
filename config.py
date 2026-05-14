import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
PORT = int(os.getenv("PORT", 10000))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 20))
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 20))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN отсутствует в .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY отсутствует в .env")
