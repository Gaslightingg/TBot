from __future__ import annotations

from bot import db
from bot.utils.mood_config import MOODS, NEGATIVE_CODES



def classify_moods(moods: list[str]) -> dict[str, object]:
    selected = list(dict.fromkeys(moods))
    negative = [mood for mood in selected if MOODS[mood]["group"] == "negative"]
    positive = [mood for mood in selected if MOODS[mood]["group"] == "positive"]
    neutral = [mood for mood in selected if MOODS[mood]["group"] == "neutral"]
    selected_set = set(selected)
    return {
        "negative": negative,
        "positive": positive,
        "neutral": neutral,
        "has_negative": bool(selected_set & NEGATIVE_CODES),
        "has_playful": "playful" in selected_set,
        "has_miss_you": "miss_you" in selected_set,
    }



def calculate_average_score(moods: list[str]) -> float:
    if not moods:
        return 0.0
    total = sum(int(MOODS[mood]["score"]) for mood in moods)
    return round(total / len(moods), 2)


async def process_mood_selection(
    db_path: str,
    telegram_id: int,
    selected_moods: list[str],
    note: str | None,
) -> dict:
    entry_id = await db.create_mood_entry(db_path, telegram_id, note)

    for mood_code in selected_moods:
        mood_meta = MOODS[mood_code]
        await db.add_mood_item(
            db_path=db_path,
            entry_id=entry_id,
            mood_code=mood_code,
            mood_label=f"{mood_meta['emoji']} {mood_meta['label']}",
            score=int(mood_meta["score"]),
        )

    flags = classify_moods(selected_moods)
    return {
        "moods": selected_moods,
        **flags,
        "avg_score": calculate_average_score(selected_moods),
    }
