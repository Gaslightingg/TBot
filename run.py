from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
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

    session = AiohttpSession(proxy=settings.telegram_proxy) if settings.telegram_proxy else AiohttpSession()
    bot = Bot(token=settings.bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(mood_router)
    dp.include_router(stats_router)

    start_scheduler(bot)

    retry_delay = 5
    attempt = 0
    try:
        while True:
            try:
                await dp.start_polling(bot)
                break
            except TelegramNetworkError as exc:
                attempt += 1
                logging.warning(
                    "Telegram network error: %s. Retrying polling in %s seconds...",
                    exc,
                    retry_delay,
                )
                if not settings.telegram_proxy:
                    logging.warning(
                        "No TELEGRAM_PROXY configured. If Telegram is blocked in your network, set TELEGRAM_PROXY in .env"
                    )
                if settings.max_polling_retries > 0 and attempt >= settings.max_polling_retries:
                    raise RuntimeError(
                        "Polling retry limit reached. Check internet access to api.telegram.org or configure TELEGRAM_PROXY."
                    ) from exc
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
            except OSError as exc:
                attempt += 1
                logging.warning(
                    "OS network error: %s. Retrying polling in %s seconds...",
                    exc,
                    retry_delay,
                )
                if settings.max_polling_retries > 0 and attempt >= settings.max_polling_retries:
                    raise RuntimeError(
                        "Polling retry limit reached. Check internet access to api.telegram.org or configure TELEGRAM_PROXY."
                    ) from exc
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
            except Exception:
                logging.exception("Unexpected fatal error while polling")
                raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
