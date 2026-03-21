"""
Конфигурация проекта «Контент-завод»
Загружает переменные окружения из .env
"""

import os
from dotenv import load_dotenv

load_dotenv()


# === Telegram ===
TG_CONTENT_BOT_TOKEN = os.getenv("TG_CONTENT_BOT_TOKEN", "")        # Бот «Контент-завод»
TG_AGENT_BOT_TOKEN = os.getenv("TG_AGENT_BOT_TOKEN", "")            # Бот AI-агент
TG_INTERVIEWER_BOT_TOKEN = os.getenv("TG_INTERVIEWER_BOT_TOKEN", "") # Бот AI-интервьюер
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID", "")                      # Канал @kuhnya154
TG_AGENT_BOT_USERNAME = os.getenv("TG_AGENT_BOT_USERNAME", "")       # Username агент-бота (для кнопки под постами)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))                          # Telegram ID Александра

# === VK ===
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))

# === AI ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# —— STT (Speech-to-Text) для голосовых правок — Groq Whisper (бесплатно) ——
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STT_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
STT_MODEL = "whisper-large-v3"

# === Модели ===
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "google/gemini-2.0-flash-001")
VISION_MODEL = os.getenv("VISION_MODEL", "google/gemini-2.0-flash-001")
RESERVE_MODEL = os.getenv("RESERVE_MODEL", "anthropic/claude-3-haiku-20240307")

# === Supabase ===
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
