from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from config import get_settings
from bot import db
from bot.utils.charts import build_monthly_chart, build_weekly_chart, calculate_stats_summary

router = Router()


async def _send_stats(message: Message, days: int) -> None:
    settings = get_settings()
    entries = await db.get_entries_by_period(settings.db_path, settings.girlfriend_id, days=days)

    if not entries:
        await message.answer("Пока нет данных за выбранный период.")
        return

    chart_path = build_weekly_chart(entries) if days == 7 else build_monthly_chart(entries)
    summary = calculate_stats_summary(entries)

    text = (
        f"Средний score: {summary['average_score']}\n"
        f"Частое настроение: {summary['most_frequent_mood']}\n"
        f"Лучший день: {summary['best_day']}\n"
        f"Худший день: {summary['worst_day']}"
    )

    await message.answer_photo(FSInputFile(chart_path), caption=text)


@router.message(Command("stats_week"))
async def stats_week(message: Message) -> None:
    await _send_stats(message, days=7)


@router.message(Command("stats_month"))
async def stats_month(message: Message) -> None:
    await _send_stats(message, days=30)
