"""
Транскрипция голосовых сообщений.
Приоритет: Groq Whisper → OpenRouter Gemini (fallback).
"""

import logging
import httpx
import base64
from bot.config import GROQ_API_KEY, STT_API_URL, STT_MODEL, OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def _transcribe_groq(audio_bytes: bytes, filename: str) -> str | None:
    """Попытка транскрибировать через Groq Whisper."""
    if not GROQ_API_KEY:
        return None

    content_type = "audio/ogg"
    if filename.endswith(".mp3"):
        content_type = "audio/mpeg"
    elif filename.endswith(".wav"):
        content_type = "audio/wav"
    elif filename.endswith(".m4a"):
        content_type = "audio/mp4"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                STT_API_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": (filename, audio_bytes, content_type)},
                data={
                    "model": STT_MODEL,
                    "language": "ru",
                    "response_format": "text",
                },
            )

            if response.status_code == 200:
                text = response.text.strip().strip('"').strip("«»").strip("'")
                logger.info(f"🎤 Groq Whisper OK: {text[:100]}...")
                return text
            else:
                logger.warning(f"🎤 Groq {response.status_code}: {response.text[:200]}")
                return None

    except Exception as e:
        logger.warning(f"🎤 Groq исключение: {e}")
        return None


async def _transcribe_openrouter(audio_bytes: bytes) -> str | None:
    """Fallback — транскрипция через OpenRouter Gemini (мультимодальная модель)."""
    if not OPENROUTER_API_KEY:
        return None

    # Кодируем аудио в base64
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Транскрибируй это голосовое сообщение на русском языке. "
                                           "Верни ТОЛЬКО текст того что сказано, без пояснений и комментариев.",
                                },
                                {
                                    "type": "input_audio",
                                    "input_audio": {
                                        "data": audio_b64,
                                        "format": "ogg",
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 2000,
                },
            )

            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                # Убираем возможные обёртки
                text = text.strip('"').strip("«»").strip("'")
                logger.info(f"🎤 OpenRouter Gemini OK: {text[:100]}...")
                return text
            else:
                logger.error(f"🎤 OpenRouter STT {response.status_code}: {response.text[:300]}")
                return None

    except Exception as e:
        logger.error(f"🎤 OpenRouter STT исключение: {e}")
        return None


async def transcribe_voice(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """Транскрибация с fallback: Groq → OpenRouter Gemini."""
    logger.info(f"🎤 Начинаю транскрипцию, размер аудио: {len(audio_bytes)} байт")

    # Попытка 1: Groq Whisper (быстро, бесплатно)
    text = await _transcribe_groq(audio_bytes, filename)
    if text:
        return text

    # Попытка 2: OpenRouter Gemini (платно, но работает)
    logger.info("🎤 Groq не сработал, пробую OpenRouter Gemini...")
    text = await _transcribe_openrouter(audio_bytes)
    if text:
        return text

    raise RuntimeError("Не удалось транскрибировать голосовое сообщение")
