"""Runtime settings, read from environment variables.

KHOJ_LLM_MODE:
  ollama  talk to a local Ollama server running Gemma (default for local dev)
  off     never call a model; use curated missions + templates only
          (the honest default for hosted demos that have no Ollama)
"""

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    db_path: Path
    llm_mode: str
    ollama_host: str
    model: str
    timeout_s: float
    frontend_dist: Path


def get_settings() -> Settings:
    data_dir = Path(os.getenv("KHOJ_DATA_DIR", ROOT / "data"))
    return Settings(
        data_dir=data_dir,
        db_path=Path(os.getenv("KHOJ_DB_PATH", data_dir / "khoj.sqlite3")),
        llm_mode=os.getenv("KHOJ_LLM_MODE", "ollama").lower(),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
        # Any Gemma tag you have pulled with `ollama pull`. Swappable on purpose.
        model=os.getenv("KHOJ_MODEL", "gemma3:4b"),
        timeout_s=float(os.getenv("KHOJ_LLM_TIMEOUT", "90")),
        frontend_dist=Path(os.getenv("KHOJ_FRONTEND_DIST", ROOT / "frontend" / "dist")),
    )
