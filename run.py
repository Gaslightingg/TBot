from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import get_settings
from bot.db import init_db
from bot.handlers.mood import router as mood_router
from bot.handlers.start import router as start_router
from bot.handlers.stats import router as stats_router
from bot.services.scheduler_service import start_scheduler


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    await init_db(settings.db_path)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(mood_router)
    dp.include_router(stats_router)

    start_scheduler(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
