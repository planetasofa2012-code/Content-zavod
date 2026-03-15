"""
Генерация изображений через OpenRouter.

Модели: Flux 2 Pro (image-only), Gemini Flash Image Preview (image+text)
Формат ответа: message.images[] содержит base64 data URLs
Документация: https://openrouter.ai/docs/features/multimodal/image-generation
"""

import logging
import httpx
import ssl
import asyncio
import base64
import re
from bot.config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Модели для генерации картинок (в порядке приоритета)
IMAGE_MODELS = [
    "black-forest-labs/flux.2-pro",       # ~$0.03/картинка, проверено
    "black-forest-labs/flux.2-klein-4b",  # ~$0.014, быстрее но проще
]

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://kuhnya54.ru",
    "X-Title": "Content-Zavod",
}

# Максимум повторов при SSL/сетевых ошибках
MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]  # секунды между попытками


def _get_modalities(model: str) -> list[str]:
    """Flux = image-only, Gemini = image+text."""
    if "flux" in model or "black-forest" in model:
        return ["image"]
    return ["image", "text"]


def _create_ssl_context() -> ssl.SSLContext:
    """Создаёт SSL-контекст, совместимый с Windows.
    
    Отключает TLS session tickets — они вызывают
    DECRYPTION_FAILED_OR_BAD_RECORD_MAC на Windows.
    """
    ctx = ssl.create_default_context()
    ctx.options |= ssl.OP_NO_TICKET  # Отключаем session tickets
    return ctx


def _extract_image_from_response(data: dict, index: int) -> bytes | None:
    """Извлекает изображение из ответа OpenRouter."""
    choices = data.get("choices", [])
    
    for choice in choices:
        msg = choice.get("message", {})

        # Формат 1: message.images[] (документация OpenRouter)
        msg_images = msg.get("images", [])
        for img_item in msg_images:
            if isinstance(img_item, dict):
                url_data = img_item.get("image_url", {}).get("url", "")
                if url_data and url_data.startswith("data:image"):
                    b64 = url_data.split(",", 1)[1]
                    img_bytes = base64.b64decode(b64)
                    logger.info(f"Image {index} OK ({len(img_bytes)} bytes)")
                    return img_bytes

        # Формат 2: content как массив с image_url
        content = msg.get("content", "")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "image_url":
                    url_data = item.get("image_url", {}).get("url", "")
                    if url_data.startswith("data:image"):
                        b64 = url_data.split(",", 1)[1]
                        img_bytes = base64.b64decode(b64)
                        logger.info(f"Image {index} OK from content list")
                        return img_bytes

        # Формат 3: content строка с base64
        if isinstance(content, str) and "data:image" in content:
            match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
            if match:
                img_bytes = base64.b64decode(match.group(1))
                logger.info(f"Image {index} OK from content string")
                return img_bytes

    return None


async def _request_with_retry(
    client: httpx.AsyncClient,
    payload: dict,
    image_index: int,
) -> bytes | None:
    """Запрос с retry при SSL/сетевых ошибках."""
    for attempt in range(MAX_RETRIES):
        try:
            response = await client.post(
                OPENROUTER_URL,
                headers=HEADERS,
                json=payload,
            )
            logger.info(f"Image {image_index}: status={response.status_code} (attempt {attempt+1})")

            if response.status_code == 200:
                data = response.json()
                img = _extract_image_from_response(data, image_index)
                if img:
                    return img
                logger.warning(f"Image {image_index}: no image in response")
                return None  # Ответ 200, но без картинки — retry не поможет
            else:
                err = response.text[:300]
                logger.error(f"Image {image_index}: {response.status_code} - {err}")
                if response.status_code >= 500:
                    # Серверная ошибка — есть смысл повторить
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAYS[attempt])
                        continue
                return None  # 4xx ошибка — retry не поможет

        except (ssl.SSLError, httpx.ConnectError, httpx.RemoteProtocolError, OSError) as e:
            logger.warning(f"Image {image_index} SSL/network error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAYS[attempt])
            else:
                logger.error(f"Image {image_index} failed after {MAX_RETRIES} retries: {e}")
                return None

        except Exception as e:
            logger.error(f"Image {image_index} unexpected error: {e}")
            return None

    return None


async def generate_images_openrouter(
    prompt: str,
    count: int = 3,
    model: str | None = None,
) -> list[bytes]:
    """
    Генерирует картинки через OpenRouter.
    
    Использует один httpx.AsyncClient для всего батча,
    retry при SSL-ошибках, и кастомный SSL-контекст для Windows.
    """
    images = []
    use_model = model or IMAGE_MODELS[0]
    ssl_ctx = _create_ssl_context()

    # Один клиент на весь батч — избегаем повторных SSL-хендшейков
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(90.0, connect=15.0),
        verify=ssl_ctx,
        http2=False,  # HTTP/2 может вызывать SSL-проблемы на Windows
    ) as client:
        for i in range(count):
            logger.info(f"Image gen {i+1}/{count} via {use_model}...")
            mods = _get_modalities(use_model)

            payload = {
                "model": use_model,
                "modalities": mods,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate image: {prompt}",
                    }
                ],
            }

            img_bytes = await _request_with_retry(client, payload, i + 1)
            
            if img_bytes:
                images.append(img_bytes)
            else:
                # Переключаемся на fallback модель
                if use_model == IMAGE_MODELS[0] and len(IMAGE_MODELS) > 1:
                    logger.info(f"Switching to fallback: {IMAGE_MODELS[1]}")
                    use_model = IMAGE_MODELS[1]

    return images


async def generate_image_prompt(post_text: str) -> str:
    """Генерирует промпт для картинки из текста поста через AI."""
    from ai.openrouter import generate_text

    prompt = f"""На основе этого текста создай промпт для генерации изображения.

Текст: {post_text[:500]}

Правила:
1. Промпт на АНГЛИЙСКОМ языке
2. Описывай конкретную сцену с мебелью в интерьере
3. Стиль: фотореалистичный, журнальная съёмка, premium
4. Без текста на картинке, без людей
5. Максимум 50 слов

Ответь ТОЛЬКО промптом, без пояснений."""

    try:
        result = await generate_text(prompt=prompt)
        return result.strip()
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        return (
            "Modern custom-made kitchen furniture, premium quality, "
            "natural lighting, interior design magazine photography, "
            "no text, no people"
        )
