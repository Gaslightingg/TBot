from __future__ import annotations

from aiogram import Bot

from bot.utils.mood_config import NEGATIVE_CODES



def format_moods(moods: list[str]) -> str:
    return ", ".join(moods)


async def send_mood_notification(bot: Bot, admin_id: int, moods: list[str]) -> None:
    text = f"У Марии сейчас:\n{format_moods(moods)}"
    await bot.send_message(admin_id, text)


async def send_alert_if_needed(bot: Bot, admin_id: int, recent_entries: list[dict]) -> None:
    if len(recent_entries) < 3:
        return

    last_three = recent_entries[:3]
    all_negative = True
    for entry in last_three:
        codes = {item["mood_code"] for item in entry.get("items", [])}
        if not (codes & NEGATIVE_CODES):
            all_negative = False
            break

    if all_negative:
        await bot.send_message(admin_id, "⚠️ Мария 3 раза подряд отмечает плохое настроение")
