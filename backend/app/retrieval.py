"""Simple local retrieval over SQLite rows.

Deliberately boring: tag/area matching plus word overlap. FAISS is only worth adding
if this stops being good enough (see docs/DECISIONS.md).
"""

import json
import random
import re
import sqlite3

_STOP = {
    "the", "and", "for", "that", "this", "with", "was", "are", "you", "why", "what",
    "how", "its", "from", "has", "have", "does", "did", "who", "when", "where", "which",
    "there", "their", "they", "them", "into", "about", "than", "then", "but", "not",
    "one", "can", "just", "very", "look", "looks", "like", "see", "saw",
}


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in _STOP}


def _rank(rows, area, interest, query_tokens, text_of):
    scored = []
    rows = list(rows)

    # Area is a hard constraint when the user selects one.
    if area:
        rows = [
            row for row in rows
            if row["area"] and row["area"].lower() == area.lower()
        ]

    random.shuffle(rows)  # variety between missions when scores tie

    for row in rows:
        interests = json.loads(row["interests"])
        overlap = len(query_tokens & tokens(text_of(row))) if query_tokens else 0

        # Interest is the primary signal within the selected area.
        score = float(overlap)

        if interest and interest != "surprise" and interest in interests:
            score += 5

        scored.append((score, overlap, row))

    scored.sort(key=lambda t: -t[0])
    return scored

def find_facts(conn: sqlite3.Connection, city: str, *, area=None, interest=None,
               query: str | None = None, k: int = 8, min_overlap: int = 0) -> list[dict]:
    rows = conn.execute("SELECT * FROM facts WHERE city = ?", (city,)).fetchall()
    q = tokens(query) if query else set()
    ranked = _rank(rows, area, interest, q, lambda r: r["text"])
    out = [dict(r) for _, overlap, r in ranked if overlap >= min_overlap]
    return out[:k]


def find_places(conn: sqlite3.Connection, city: str, *, area=None, interest=None,
                k: int = 6) -> list[dict]:
    rows = conn.execute("SELECT * FROM places WHERE city = ?", (city,)).fetchall()
    ranked = _rank(rows, area, interest, set(), lambda r: r["summary"])
    return [dict(r) for _, _, r in ranked][:k]
