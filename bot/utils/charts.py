from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt



def calculate_stats_summary(entries: list[dict]) -> dict[str, str | float]:
    if not entries:
        return {
            "average_score": 0.0,
            "most_frequent_mood": "нет данных",
            "best_day": "нет данных",
            "worst_day": "нет данных",
        }

    day_scores: dict[str, list[float]] = defaultdict(list)
    moods_counter: Counter[str] = Counter()

    for entry in entries:
        date_key = entry["created_at"][:10]
        item_scores = [item["score"] for item in entry.get("items", [])]
        if item_scores:
            day_scores[date_key].append(sum(item_scores) / len(item_scores))
        for item in entry.get("items", []):
            moods_counter[item["mood_label"]] += 1

    avg_by_day = {day: sum(values) / len(values) for day, values in day_scores.items()}
    overall_avg = round(sum(avg_by_day.values()) / len(avg_by_day), 2) if avg_by_day else 0.0

    best_day = max(avg_by_day, key=avg_by_day.get) if avg_by_day else "нет данных"
    worst_day = min(avg_by_day, key=avg_by_day.get) if avg_by_day else "нет данных"
    frequent = moods_counter.most_common(1)[0][0] if moods_counter else "нет данных"

    return {
        "average_score": overall_avg,
        "most_frequent_mood": frequent,
        "best_day": best_day,
        "worst_day": worst_day,
    }



def _build_line_chart(entries: list[dict], title: str, filepath: str) -> str:
    day_scores: dict[str, list[float]] = defaultdict(list)

    for entry in entries:
        date_key = entry["created_at"][:10]
        scores = [item["score"] for item in entry.get("items", [])]
        if scores:
            day_scores[date_key].append(sum(scores) / len(scores))

    sorted_days = sorted(day_scores.keys(), key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
    avg_scores = [sum(day_scores[day]) / len(day_scores[day]) for day in sorted_days]

    plt.figure(figsize=(10, 4))
    plt.plot(sorted_days, avg_scores, marker="o", color="#ff5f87")
    plt.title(title)
    plt.xlabel("Дата")
    plt.ylabel("Score")
    plt.ylim(0.5, 5.1)
    plt.grid(alpha=0.3)
    plt.xticks(rotation=35)
    plt.tight_layout()

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath



def build_weekly_chart(entries: list[dict]) -> str:
    return _build_line_chart(entries, "Настроение за неделю", "data/weekly_chart.png")



def build_monthly_chart(entries: list[dict]) -> str:
    return _build_line_chart(entries, "Настроение за месяц", "data/monthly_chart.png")
