"""
Точка входа: запуск всех ботов «Контент-завод».
MVP: контент-бот (Александр) + AI-агент (клиенты).
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import TG_CONTENT_BOT_TOKEN, TG_AGENT_BOT_TOKEN
from bot.content_bot.handlers import router as content_router
from bot.agent_bot.handlers import router as agent_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск всех ботов."""
    logger.info("🏭 Контент-завод: запуск...")

    bots = []
    tasks = []

    # === Контент-бот (для Александра) ===
    if TG_CONTENT_BOT_TOKEN:
        content_bot = Bot(token=TG_CONTENT_BOT_TOKEN)
        content_dp = Dispatcher(storage=MemoryStorage())
        content_dp.include_router(content_router)
        bots.append(content_bot)
        tasks.append(content_dp.start_polling(content_bot))
        logger.info("✅ Контент-бот запущен")

    # === AI-агент (для клиентов) ===
    if TG_AGENT_BOT_TOKEN:
        agent_bot = Bot(token=TG_AGENT_BOT_TOKEN)
        agent_dp = Dispatcher(storage=MemoryStorage())
        agent_dp.include_router(agent_router)
        bots.append(agent_bot)
        tasks.append(agent_dp.start_polling(agent_bot))
        logger.info("✅ AI-агент запущен")

    # Запуск всех ботов параллельно
    try:
        await asyncio.gather(*tasks)
    finally:
        for bot in bots:
            await bot.session.close()
        logger.info("🏭 Контент-завод: остановлен")


if __name__ == "__main__":
    asyncio.run(main())
