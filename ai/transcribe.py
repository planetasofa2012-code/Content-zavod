"""
Транскрипция голосовых сообщений через Groq Whisper API (бесплатно).
Если Groq недоступен — фоллбэк на OpenAI Whisper.
"""

import logging
import httpx
from bot.config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


async def transcribe_voice(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """Транскрибирует голосовое сообщение в текст."""

    # Пробуем через OpenRouter (поддерживает аудио модели)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                files={"file": (filename, audio_bytes, "audio/ogg")},
                data={"model": "openai/whisper-large-v3"},
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "")
                logger.info(f"🎤 Транскрипция через OpenRouter: {text[:50]}...")
                return text

    except Exception as e:
        logger.warning(f"OpenRouter Whisper не доступен: {e}")

    # Фоллбэк: Groq бесплатный Whisper
    try:
        groq_key = OPENROUTER_API_KEY  # Если есть отдельный ключ Groq, можно заменить
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_WHISPER_URL,
                headers={"Authorization": f"Bearer {groq_key}"},
                files={"file": (filename, audio_bytes, "audio/ogg")},
                data={
                    "model": "whisper-large-v3",
                    "language": "ru",
                },
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "")
                logger.info(f"🎤 Транскрипция через Groq: {text[:50]}...")
                return text

    except Exception as e:
        logger.warning(f"Groq Whisper не доступен: {e}")

    raise RuntimeError("Не удалось транскрибировать голосовое сообщение")
