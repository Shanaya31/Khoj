import json

import pytest
from app.city_pack import CityPack, list_city_dirs, load_city_pack
from app.config import ROOT
from pydantic import ValidationError


def test_every_shipped_pack_is_valid():
    dirs = list_city_dirs(ROOT / "data")
    assert dirs, "expected at least the Mumbai pack"
    for d in dirs:
        pack = load_city_pack(d)
        assert pack.meta.city == d.name
        assert len(pack.missions) >= 5


def test_mumbai_pack_covers_every_interest_and_duration():
    pack = load_city_pack(ROOT / "data" / "cities" / "mumbai")
    interests = {m.interest for m in pack.missions}
    assert {"history", "architecture", "nature", "art", "local_life", "hidden_details"} <= interests
    assert {m.duration_minutes for m in pack.missions} >= {20, 45, 90, 120}


def test_pack_rejects_dangling_references():
    d = ROOT / "data" / "cities" / "mumbai"
    raw = {
        "meta": json.loads((d / "pack.json").read_text()),
        "places": json.loads((d / "places.json").read_text()),
        "facts": json.loads((d / "history.json").read_text()),
        "missions": json.loads((d / "missions.json").read_text()),
    }
    raw["facts"][0]["place_id"] = "does-not-exist"
    with pytest.raises(ValidationError):
        CityPack(**raw)
