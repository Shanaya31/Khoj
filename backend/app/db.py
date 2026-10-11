"""SQLite storage. Works offline, needs no server."""

import json
import sqlite3
from pathlib import Path

from .city_pack import CityPack

SCHEMA = """
CREATE TABLE IF NOT EXISTS places (
  city TEXT, id TEXT, name TEXT, area TEXT, interests TEXT, lat REAL, lon REAL,
  summary TEXT, observation_prompt TEXT, PRIMARY KEY (city, id));
CREATE TABLE IF NOT EXISTS facts (
  city TEXT, id TEXT, area TEXT, text TEXT, interests TEXT, place_id TEXT,
  source TEXT, verified INTEGER, PRIMARY KEY (city, id));
CREATE TABLE IF NOT EXISTS missions (
  city TEXT, id TEXT, title TEXT, interest TEXT, duration_minutes INTEGER,
  intro TEXT, objectives TEXT, PRIMARY KEY (city, id));
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY, city TEXT, area TEXT, interest TEXT, duration_minutes INTEGER,
  mission TEXT, mission_source TEXT, created_at TEXT, finished_at TEXT, journal TEXT);
CREATE TABLE IF NOT EXISTS observations (
  id TEXT PRIMARY KEY, session_id TEXT, text TEXT, question TEXT, lat REAL, lon REAL,
  explanation TEXT, fact_ids TEXT, created_at TEXT);
"""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def seed_city(conn: sqlite3.Connection, pack: CityPack) -> None:
    """Replace one city's knowledge. Sessions and observations are never touched."""
    city = pack.meta.city
    for table in ("places", "facts", "missions"):
        conn.execute(f"DELETE FROM {table} WHERE city = ?", (city,))
    conn.executemany(
        "INSERT INTO places VALUES (?,?,?,?,?,?,?,?,?)",
        [
            (city, p.id, p.name, p.area, json.dumps(p.interests), p.lat, p.lon,
             p.summary, p.observation_prompt)
            for p in pack.places
        ],
    )
    conn.executemany(
        "INSERT INTO facts VALUES (?,?,?,?,?,?,?,?)",
        [
            (city, f.id, f.area, f.text, json.dumps(f.interests), f.place_id,
             f.source, int(f.verified))
            for f in pack.facts
        ],
    )
    conn.executemany(
        "INSERT INTO missions VALUES (?,?,?,?,?,?,?)",
        [
            (city, m.id, m.title, m.interest, m.duration_minutes, m.intro,
             json.dumps(m.objectives))
            for m in pack.missions
        ],
    )
    conn.commit()
