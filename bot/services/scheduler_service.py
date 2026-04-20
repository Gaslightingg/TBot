from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from aiogram import Bot

from config import get_settings
from bot.keyboards import build_mood_keyboard


async def send_daily_reminder(bot: Bot, telegram_id: int) -> None:
    await bot.send_message(
        telegram_id,
        "Как ты себя чувствуешь сейчас?",
        reply_markup=build_mood_keyboard(selected=[]),
    )


async def _scheduler_loop(bot: Bot) -> None:
    settings = get_settings()
    while True:
        now = datetime.utcnow()
        target = now.replace(
            hour=settings.reminder_hour_utc,
            minute=settings.reminder_minute_utc,
            second=0,
            microsecond=0,
        )
        if target <= now:
            target += timedelta(days=1)

        await asyncio.sleep((target - now).total_seconds())
        await send_daily_reminder(bot, settings.girlfriend_id)



def start_scheduler(bot: Bot) -> asyncio.Task:
    return asyncio.create_task(_scheduler_loop(bot))
