from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards import build_mood_keyboard, build_start_keyboard

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    await message.answer(
        "Привет, любимая 💖 Я рядом. Нажми кнопку ниже и выбери настроение.",
        reply_markup=build_start_keyboard(),
    )


@router.callback_query(F.data == "open_mood")
async def open_mood(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Выбери одно или несколько настроений:",
        reply_markup=build_mood_keyboard(selected=[]),
    )
    await callback.answer()
