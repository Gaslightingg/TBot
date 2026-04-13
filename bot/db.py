from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

import aiosqlite


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS mood_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mood_entry_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mood_entry_id INTEGER NOT NULL,
    mood_code TEXT NOT NULL,
    mood_label TEXT NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY(mood_entry_id) REFERENCES mood_entries(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mood_entries_telegram_id ON mood_entries(telegram_id);
CREATE INDEX IF NOT EXISTS idx_mood_entries_created_at ON mood_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_mood_items_entry_id ON mood_entry_items(mood_entry_id);
"""


async def get_connection(db_path: str) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn


async def init_db(db_path: str) -> None:
    async with await get_connection(db_path) as conn:
        await conn.executescript(SCHEMA_SQL)
        await conn.commit()


async def create_mood_entry(db_path: str, telegram_id: int, note: str | None) -> int:
    async with await get_connection(db_path) as conn:
        cursor = await conn.execute(
            "INSERT INTO mood_entries (telegram_id, note) VALUES (?, ?)",
            (telegram_id, note),
        )
        await conn.commit()
        return int(cursor.lastrowid)


async def add_mood_item(
    db_path: str,
    entry_id: int,
    mood_code: str,
    mood_label: str,
    score: int,
) -> None:
    async with await get_connection(db_path) as conn:
        await conn.execute(
            """
            INSERT INTO mood_entry_items (mood_entry_id, mood_code, mood_label, score)
            VALUES (?, ?, ?, ?)
            """,
            (entry_id, mood_code, mood_label, score),
        )
        await conn.commit()


async def get_entries_by_period(db_path: str, telegram_id: int, days: int) -> list[dict]:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    async with await get_connection(db_path) as conn:
        rows = await conn.execute_fetchall(
            """
            SELECT me.id, me.telegram_id, me.note, me.created_at,
                   mei.mood_code, mei.mood_label, mei.score
            FROM mood_entries me
            JOIN mood_entry_items mei ON mei.mood_entry_id = me.id
            WHERE me.telegram_id = ? AND me.created_at >= ?
            ORDER BY me.created_at ASC, mei.id ASC
            """,
            (telegram_id, since),
        )
    return _group_entries(rows)


async def get_last_entries(db_path: str, telegram_id: int, limit: int) -> list[dict]:
    async with await get_connection(db_path) as conn:
        entry_rows = await conn.execute_fetchall(
            """
            SELECT id, telegram_id, note, created_at
            FROM mood_entries
            WHERE telegram_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (telegram_id, limit),
        )

        if not entry_rows:
            return []

        entry_ids = [row["id"] for row in entry_rows]
        placeholders = ",".join(["?"] * len(entry_ids))
        items = await conn.execute_fetchall(
            f"""
            SELECT mood_entry_id, mood_code, mood_label, score
            FROM mood_entry_items
            WHERE mood_entry_id IN ({placeholders})
            ORDER BY id ASC
            """,
            tuple(entry_ids),
        )

    items_by_entry: dict[int, list[dict]] = defaultdict(list)
    for item in items:
        items_by_entry[item["mood_entry_id"]].append(
            {
                "mood_code": item["mood_code"],
                "mood_label": item["mood_label"],
                "score": item["score"],
            }
        )

    return [
        {
            "id": row["id"],
            "telegram_id": row["telegram_id"],
            "note": row["note"],
            "created_at": row["created_at"],
            "items": items_by_entry.get(row["id"], []),
        }
        for row in entry_rows
    ]



def _group_entries(rows: list[aiosqlite.Row]) -> list[dict]:
    grouped: dict[int, dict] = {}
    for row in rows:
        entry_id = row["id"]
        if entry_id not in grouped:
            grouped[entry_id] = {
                "id": entry_id,
                "telegram_id": row["telegram_id"],
                "note": row["note"],
                "created_at": row["created_at"],
                "items": [],
            }
        grouped[entry_id]["items"].append(
            {
                "mood_code": row["mood_code"],
                "mood_label": row["mood_label"],
                "score": row["score"],
            }
        )
    return list(grouped.values())
