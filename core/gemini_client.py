import os
import time
import logging
from typing import List, Dict
import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not GEMINI_API_KEY or not GEMINI_API_KEY.startswith("AI"):
    raise ValueError("❌ GEMINI_API_KEY отсутствует или неправильный")

genai.configure(api_key=GEMINI_API_KEY)

# Используем модель, которая точно работает в этом окружении
MODEL_NAME = "gemini-flash-latest"

# Основной system prompt — здесь весь новый стиль
SYSTEM_PROMPT = (
    "Ты мой друг и помощник в телеге. "
    "Отвечай очень просто, коротко и по-человечески, как будто пишешь в обычном чате. "
    "Максимум 2-3 предложения. "
    "Говори живым языком, без официоза. "
    "Запрещено: markdown, звездочки, жирный текст, списки, нумерация, заголовки, "
    "таблицы, длинные объяснения, лекции и лишние символы. "
    "Пиши обычным текстом, коротко и по делу."
)

def _truncate_history(history: List[Dict], max_messages: int = 10):
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]

def _clean_text(text: str) -> str:
    """Убираем остатки оформления"""
    # Удаляем символы разметки
    for char in ["**", "__", "`", "#", "*", "•"]:
        text = text.replace(char, "")
    # Убираем цифры списков в начале строк
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and line[1:3] == ". ":
            line = line[3:]
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def ask_gemini(system_prompt: str, history: list, user_message: str) -> str:
    # Используем строгий стиль, если промпт не передан явно
    final_system_prompt = system_prompt if system_prompt else SYSTEM_PROMPT

    gemini_history = []
    for msg in _truncate_history(history):
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    try:
        working_model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=final_system_prompt
        )

        chat = working_model.start_chat(history=gemini_history)

        for attempt in range(3):
            try:
                response = chat.send_message(
                    user_message,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=800,
                        temperature=0.9,
                        top_p=0.95
                    ),
                    request_options={"timeout": 20}
                )
                
                answer = _clean_text(response.text)
                
                if not answer:
                    return "Не понял, повтори ещё раз"
                    
                logger.debug(f"Gemini ответил: {answer[:60]}...")
                return answer

            except Exception as e:
                logger.warning(f"Gemini attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)
    except Exception as e:
        logger.error(f"Критическая ошибка Gemini: {e}")

    return "Ща, секунду, что-то подвисло. Напиши ещё раз."

def describe_image(image_bytes: bytes, prompt: str = "Опиши это изображение просто и коротко на русском языке") -> str:
    import PIL.Image, io
    try:
        vision_model = genai.GenerativeModel(MODEL_NAME)
        img = PIL.Image.open(io.BytesIO(image_bytes))
        # Применяем тот же стиль к зрению
        response = vision_model.generate_content([
            f"{SYSTEM_PROMPT}\n\nЗадание: {prompt}", 
            img
        ])
        return _clean_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {e}")
        return "⚠️ Не удалось разобрать картинку."
