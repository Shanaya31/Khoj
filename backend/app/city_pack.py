"""City packs: the contribution surface of Khoj.

A pack is a folder of plain JSON files under data/cities/<city>/:

  pack.json                  metadata + list of areas
  places.json                places worth noticing
  history.json               short, checkable facts (the AI may only use these)
  missions.json              hand-written missions (also the offline fallback)
  observation_prompts.json   gentle nudges shown while exploring

Nobody needs to understand the AI layer to add a city.
"""

import json
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from .schemas import Duration, Interest


class PackMeta(BaseModel):
    city: str  # slug, must equal the folder name
    display_name: str
    country: str
    version: str
    areas: list[str]
    description: str = ""
    coords_approximate: bool = True


class Place(BaseModel):
    id: str
    name: str
    area: str
    interests: list[Interest]
    lat: float
    lon: float
    summary: str
    observation_prompt: str | None = None


class Fact(BaseModel):
    id: str
    area: str | None = None
    text: str
    interests: list[Interest]
    place_id: str | None = None
    source: str | None = None
    verified: bool = False


class CuratedMission(BaseModel):
    id: str
    title: str
    interest: Interest
    duration_minutes: Duration
    intro: str = ""
    objectives: list[str] = Field(min_length=3, max_length=6)


class CityPack(BaseModel):
    meta: PackMeta
    places: list[Place]
    facts: list[Fact]
    missions: list[CuratedMission]
    observation_prompts: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_references(self) -> "CityPack":
        for label, items in (
            ("place", self.places),
            ("fact", self.facts),
            ("mission", self.missions),
        ):
            ids = [i.id for i in items]
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate {label} ids in pack {self.meta.city}")
        place_ids = {p.id for p in self.places}
        areas = set(self.meta.areas)
        for p in self.places:
            if p.area not in areas:
                raise ValueError(f"place {p.id}: area {p.area!r} not listed in pack.json")
        for f in self.facts:
            if f.place_id and f.place_id not in place_ids:
                raise ValueError(f"fact {f.id}: unknown place_id {f.place_id!r}")
            if f.area and f.area not in areas:
                raise ValueError(f"fact {f.id}: area {f.area!r} not listed in pack.json")
        return self


def _read(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_city_pack(city_dir: Path) -> CityPack:
    pack = CityPack(
        meta=_read(city_dir / "pack.json"),
        places=_read(city_dir / "places.json"),
        facts=_read(city_dir / "history.json"),
        missions=_read(city_dir / "missions.json"),
        observation_prompts=_read(city_dir / "observation_prompts.json"),
    )
    if pack.meta.city != city_dir.name:
        raise ValueError(f"pack.json city {pack.meta.city!r} != folder {city_dir.name!r}")
    return pack


def list_city_dirs(data_dir: Path) -> list[Path]:
    root = data_dir / "cities"
    if not root.is_dir():
        return []
    return sorted(d for d in root.iterdir() if (d / "pack.json").is_file())
