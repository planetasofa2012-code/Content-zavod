"""
Настройка окружения для тестов.
Устанавливаем переменные окружения ДО импорта bot.config,
чтобы не получить ошибки при int() преобразовании.
"""
import os

os.environ.setdefault("OWNER_ID", "0")
os.environ.setdefault("VK_GROUP_ID", "0")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-for-tests")
os.environ.setdefault("DEFAULT_MODEL", "google/gemini-2.0-flash-001")
os.environ.setdefault("VISION_MODEL", "google/gemini-2.0-flash-001")
os.environ.setdefault("RESERVE_MODEL", "anthropic/claude-3-haiku-20240307")
os.environ.setdefault("TG_CHANNEL_ID", "")
os.environ.setdefault("TG_AGENT_BOT_TOKEN", "")
os.environ.setdefault("TG_CONTENT_BOT_TOKEN", "")
