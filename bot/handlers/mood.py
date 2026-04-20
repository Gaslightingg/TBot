from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import get_settings
from bot import db
from bot.keyboards import build_mood_keyboard, build_note_keyboard
from bot.services.mood_service import process_mood_selection
from bot.services.notification_service import send_alert_if_needed, send_mood_notification
from bot.texts import generate_response
from bot.utils.mood_config import MOODS, mood_display

router = Router()


class MoodStates(StatesGroup):
    selecting = State()
    waiting_note = State()


@router.callback_query(F.data.startswith("mood_toggle:"))
async def toggle_mood(callback: CallbackQuery, state: FSMContext) -> None:
    mood_code = callback.data.split(":", maxsplit=1)[1]

    if mood_code not in MOODS:
        await callback.answer("Неизвестное настроение", show_alert=True)
        return

    data = await state.get_data()
    selected = data.get("selected_moods", [])

    if mood_code in selected:
        selected.remove(mood_code)
    else:
        selected.append(mood_code)

    await state.update_data(selected_moods=selected)
    await state.set_state(MoodStates.selecting)
    await callback.message.edit_reply_markup(reply_markup=build_mood_keyboard(selected=selected))
    await callback.answer()


@router.callback_query(F.data == "mood_done")
async def finish_mood_select(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected: list[str] = data.get("selected_moods", [])

    if not selected:
        await callback.message.answer("Выбери хотя бы одно настроение")
        await callback.answer()
        return

    await callback.message.answer(
        "Хочешь добавить комментарий к записи? Напиши текст или нажми «Пропустить комментарий».",
        reply_markup=build_note_keyboard(),
    )
    await state.set_state(MoodStates.waiting_note)
    await callback.answer()


@router.callback_query(F.data == "note_skip", MoodStates.waiting_note)
async def skip_note(callback: CallbackQuery, state: FSMContext) -> None:
    await _save_and_respond(callback.message, state, note=None)
    await callback.answer()


@router.message(MoodStates.waiting_note)
async def save_note(message: Message, state: FSMContext) -> None:
    await _save_and_respond(message, state, note=message.text or "")


async def _save_and_respond(message: Message, state: FSMContext, note: str | None) -> None:
    settings = get_settings()
    selected = (await state.get_data()).get("selected_moods", [])
    if message.from_user is None:
        return

    result = await process_mood_selection(
        db_path=settings.db_path,
        telegram_id=message.from_user.id,
        selected_moods=selected,
        note=note,
    )

    await message.answer(generate_response(result["moods"]))

    mood_labels = [mood_display(code) for code in result["moods"]]
    await send_mood_notification(message.bot, settings.admin_id, mood_labels)

    recent_entries = await db.get_last_entries(settings.db_path, message.from_user.id, limit=3)
    await send_alert_if_needed(message.bot, settings.admin_id, recent_entries)

    await message.answer(
        f"Сохранил 💌\nВыбрано: {', '.join(mood_labels)}\nСредний score: {result['avg_score']}"
    )
    await state.clear()
