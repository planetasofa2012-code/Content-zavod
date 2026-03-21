"""
Транскрипция голосовых сообщений через Groq Whisper Large V3.
Groq предоставляет аппаратное ускорение (LPU) — бесплатно и очень быстро.
"""

import logging
import httpx
from bot.config import GROQ_API_KEY, STT_API_URL, STT_MODEL

logger = logging.getLogger(__name__)


async def transcribe_voice(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """Транскрибирует голосовое сообщение через Groq Whisper API."""

    logger.info(f"🎤 Начинаю транскрипцию (Groq Whisper), размер аудио: {len(audio_bytes)} байт")

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY не задан в .env — транскрипция невозможна")

    # Определяем MIME-тип для multipart-загрузки
    content_type = "audio/ogg"
    if filename.endswith(".mp3"):
        content_type = "audio/mpeg"
    elif filename.endswith(".wav"):
        content_type = "audio/wav"
    elif filename.endswith(".m4a"):
        content_type = "audio/mp4"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Whisper API принимает файл через multipart/form-data
            response = await client.post(
                STT_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                },
                files={
                    "file": (filename, audio_bytes, content_type),
                },
                data={
                    "model": STT_MODEL,
                    "language": "ru",
                    "response_format": "text",
                },
            )

            logger.info(f"🎤 Groq Whisper ответ: status={response.status_code}")

            if response.status_code == 200:
                text = response.text.strip()
                # Убираем кавычки если модель обернула
                text = text.strip('"').strip("«»").strip("'")
                logger.info(f"🎤 Транскрипция: {text[:100]}...")
                return text
            else:
                logger.error(f"🎤 Ошибка Groq {response.status_code}: {response.text[:500]}")

    except httpx.TimeoutException:
        logger.error("🎤 Таймаут Groq Whisper (30 сек)")
    except Exception as e:
        logger.error(f"🎤 Исключение при транскрипции: {e}")

    raise RuntimeError("Не удалось транскрибировать голосовое сообщение")
