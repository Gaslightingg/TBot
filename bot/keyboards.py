from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.mood_config import MOODS, mood_display



def build_mood_keyboard(selected: list[str]) -> InlineKeyboardMarkup:
    selected_set = set(selected)
    rows: list[list[InlineKeyboardButton]] = []

    for mood_code in MOODS:
        title = mood_display(mood_code)
        if mood_code in selected_set:
            title = f"✓ {title}"
        rows.append([InlineKeyboardButton(text=title, callback_data=f"mood_toggle:{mood_code}")])

    rows.append([InlineKeyboardButton(text="Готово", callback_data="mood_done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)



def build_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Выбрать настроение", callback_data="open_mood")]]
    )



def build_note_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Пропустить комментарий", callback_data="note_skip")]]
    )
