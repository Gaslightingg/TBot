# Telegram Mood Tracker Bot (aiogram 3)

Бот для трекинга настроения девушки с multi-select выбором настроений, комментариями, SQLite-хранилищем, графиками и уведомлениями администратору.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

1. Создайте `.env`:

```bash
cp .env.example .env
```

2. Заполните переменные:

- `BOT_TOKEN` — токен бота
- `ADMIN_ID` — Telegram ID администратора
- `GIRLFRIEND_ID` — Telegram ID девушки
- `DB_PATH` — путь к SQLite (по умолчанию `data/mood_tracker.db`)
- `REMINDER_HOUR_UTC`, `REMINDER_MINUTE_UTC` — время ежедневного напоминания (UTC)

## Запуск

```bash
python run.py
```

## Структура

```text
run.py
config.py
bot/
  db.py
  keyboards.py
  texts.py
  handlers/
    start.py
    mood.py
    stats.py
  services/
    mood_service.py
    notification_service.py
    scheduler_service.py
  utils/
    mood_config.py
    charts.py
```

## Команды

- `/start` — приветствие + кнопка «Выбрать настроение»
- `/stats_week` — график за 7 дней
- `/stats_month` — график за 30 дней
