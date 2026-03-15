"""
AI-движок: клиент OpenRouter API
Работает с Gemini Flash (основная), Claude Haiku (резерв)
"""

import httpx
import ssl
import base64
import logging
from bot.config import OPENROUTER_API_KEY, DEFAULT_MODEL, VISION_MODEL, RESERVE_MODEL

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://kuhnya54.ru",
    "X-Title": "Content-Zavod",
}


def _create_ssl_context() -> ssl.SSLContext:
    """SSL-контекст для Windows — без session tickets."""
    ctx = ssl.create_default_context()
    ctx.options |= ssl.OP_NO_TICKET
    return ctx


async def chat(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Отправить запрос в AI-модель через OpenRouter."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(
            timeout=30,
            verify=_create_ssl_context(),
            http2=False,
        ) as client:
            response = await client.post(OPENROUTER_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenRouter error ({model}): {e}")
        # Попробовать резервную модель
        if model != RESERVE_MODEL:
            logger.info(f"Пробую резервную модель: {RESERVE_MODEL}")
            return await chat(messages, model=RESERVE_MODEL, temperature=temperature, max_tokens=max_tokens)
        raise


async def chat_with_vision(
    text: str,
    image_bytes: bytes,
    system_prompt: str = "",
    model: str = VISION_MODEL,
) -> str:
    """Отправить запрос с изображением (Vision API)."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}",
                },
            },
            {
                "type": "text",
                "text": text,
            },
        ],
    })

    return await chat(messages, model=model)


async def generate_text(
    prompt: str,
    system_prompt: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
) -> str:
    """Простая генерация текста."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    return await chat(messages, model=model, temperature=temperature)
