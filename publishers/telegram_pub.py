"""
Публикатор: Telegram-канал.
Отправляет пост с фото в канал @kuhnya154.
Каждый пост снабжается CTA-кнопкой → клиент переходит в AI-агент бот.
"""

import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import TG_CHANNEL_ID, TG_AGENT_BOT_USERNAME

logger = logging.getLogger(__name__)


def _get_channel_keyboard() -> InlineKeyboardMarkup | None:
    """CTA-кнопка под постами канала → агент-бот."""
    if not TG_AGENT_BOT_USERNAME:
        logger.warning("TG_AGENT_BOT_USERNAME не задан — кнопка под постом не добавлена")
        return None

    # deep-link: клиент нажимает → открывается агент-бот с параметром from_channel
    bot_url = f"https://t.me/{TG_AGENT_BOT_USERNAME}?start=from_channel"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔥 Хочу такую! Узнать цену",
            url=bot_url,
        )],
    ])


async def publish_to_telegram(bot: Bot, photo_file_id: str, text: str) -> bool:
    """Публикует пост в Telegram-канал с CTA-кнопкой."""
    if not TG_CHANNEL_ID:
        raise ValueError("TG_CHANNEL_ID не настроен в .env")

    try:
        # Обрезаем текст до 1024 символов (лимит caption)
        if len(text) > 1024:
            text = text[:1020] + "..."

        await bot.send_photo(
            chat_id=TG_CHANNEL_ID,
            photo=photo_file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=_get_channel_keyboard(),
        )
        logger.info(f"Опубликовано в Telegram-канал {TG_CHANNEL_ID} (с CTA-кнопкой)")
        return True
    except Exception as e:
        logger.error(f"Ошибка публикации в Telegram: {e}")
        raise
