from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    bot_token: str
    admin_id: int
    girlfriend_id: int
    db_path: str = "data/mood_tracker.db"
    reminder_hour_utc: int = 9
    reminder_minute_utc: int = 0
    telegram_proxy: str | None = None
    max_polling_retries: int = 0



def get_settings() -> Settings:
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_id = int(os.getenv("ADMIN_ID", "0"))
    girlfriend_id = int(os.getenv("GIRLFRIEND_ID", "0"))
    db_path = os.getenv("DB_PATH", "data/mood_tracker.db")
    reminder_hour_utc = int(os.getenv("REMINDER_HOUR_UTC", "9"))
    reminder_minute_utc = int(os.getenv("REMINDER_MINUTE_UTC", "0"))
    telegram_proxy = os.getenv("TELEGRAM_PROXY", "").strip() or None
    max_polling_retries = int(os.getenv("MAX_POLLING_RETRIES", "0"))

    if not bot_token:
        raise ValueError("BOT_TOKEN is required")
    if admin_id <= 0:
        raise ValueError("ADMIN_ID is required")
    if girlfriend_id <= 0:
        raise ValueError("GIRLFRIEND_ID is required")

    return Settings(
        bot_token=bot_token,
        admin_id=admin_id,
        girlfriend_id=girlfriend_id,
        db_path=db_path,
        reminder_hour_utc=reminder_hour_utc,
        reminder_minute_utc=reminder_minute_utc,
        telegram_proxy=telegram_proxy,
        max_polling_retries=max_polling_retries,
    )
