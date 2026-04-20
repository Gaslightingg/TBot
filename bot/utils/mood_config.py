from __future__ import annotations

MOODS: dict[str, dict[str, str | int]] = {
    "great": {"emoji": "😄", "label": "Отлично", "score": 5, "group": "positive"},
    "good": {"emoji": "🙂", "label": "Хорошо", "score": 4, "group": "positive"},
    "normal": {"emoji": "😐", "label": "Нормально", "score": 3, "group": "neutral"},
    "sad": {"emoji": "😔", "label": "Грустно", "score": 2, "group": "negative"},
    "angry": {"emoji": "😡", "label": "Злюсь", "score": 1, "group": "negative"},
    "tired": {"emoji": "😴", "label": "Устала", "score": 2, "group": "negative"},
    "anxious": {"emoji": "😰", "label": "Тревожно", "score": 1, "group": "negative"},
    "loved": {"emoji": "❤️", "label": "Любимо", "score": 5, "group": "positive"},
    "playful": {"emoji": "😏", "label": "Игривое", "score": 4, "group": "positive"},
    "miss_you": {"emoji": "🥺", "label": "Скучаю", "score": 3, "group": "neutral"},
}

NEGATIVE_CODES = {code for code, meta in MOODS.items() if meta["group"] == "negative"}
POSITIVE_CODES = {code for code, meta in MOODS.items() if meta["group"] == "positive"}



def mood_display(code: str) -> str:
    mood = MOODS[code]
    return f"{mood['emoji']} {mood['label']}"
