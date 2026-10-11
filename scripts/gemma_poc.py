#!/usr/bin/env python3
"""Milestone 1: prove Gemma can produce a valid, grounded Mumbai mission locally.

    ollama pull gemma3:4b
    python scripts/gemma_poc.py --area Fort --minutes 45 --interest architecture

Exit code 0 only if the *model* (not the curated fallback) produced a valid mission.
"""

import argparse
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.city_pack import load_city_pack  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db import init_db, seed_city  # noqa: E402
from app.llm import OllamaLLM  # noqa: E402
from app.schemas import MissionRequest  # noqa: E402
from app.services import generate_mission  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--area", default="Fort")
    ap.add_argument("--minutes", type=int, default=45, choices=[20, 45, 90, 120])
    ap.add_argument("--interest", default="architecture")
    args = ap.parse_args()

    s = get_settings()
    llm = OllamaLLM(s.ollama_host, s.model, s.timeout_s)
    print(f"Ollama: {s.ollama_host}  model: {s.model}  reachable: {llm.ping()}")

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    seed_city(conn, load_city_pack(ROOT / "data" / "cities" / "mumbai"))

    req = MissionRequest(area=args.area, duration_minutes=args.minutes, interest=args.interest)
    t0 = time.perf_counter()
    mission, source = generate_mission(conn, llm, req)
    print(f"source: {source}   latency: {time.perf_counter() - t0:.1f}s\n")
    print(mission.model_dump_json(indent=2))
    return 0 if source == "gemma" else 1


if __name__ == "__main__":
    raise SystemExit(main())
