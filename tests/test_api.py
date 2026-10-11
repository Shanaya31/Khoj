from app.llm import LLMError
from conftest import FakeLLM

GOOD_MISSION = {
    "title": "Gothic Fort",
    "intro": "Look up.",
    "objectives": [
        {"text": "Find a carved face", "fact_ids": ["f_csmt_1", "made-up"], "place_id": "nope"},
        {"text": "Find a tower"},
        {"text": "Find a date carved in stone"},
    ],
    "closing": "Phone away.",
}
REQ = {"city": "mumbai", "area": "Fort", "duration_minutes": 45, "interest": "architecture"}


def test_health_and_cities(make_client):
    c = make_client()
    body = c.get("/api/health").json()
    assert body["status"] == "ok" and "mumbai" in body["cities"]
    assert c.get("/api/cities").json()[0]["display_name"] == "Mumbai"


def test_city_pack_download_and_bad_names(make_client):
    c = make_client()
    pack = c.get("/api/city-pack/mumbai").json()
    assert {"meta", "places", "facts", "missions"} <= pack.keys()
    assert c.get("/api/city-pack/atlantis").status_code == 404
    assert c.get("/api/city-pack/..%2Fetc").status_code in (404, 422)


def test_mission_without_model_uses_curated_pack(make_client):
    r = make_client().post("/api/mission", json=REQ)
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "curated"
    assert 3 <= len(body["mission"]["objectives"]) <= 6
    assert body["session_id"]


def test_mission_from_model_drops_invented_citations(make_client):
    llm = FakeLLM(GOOD_MISSION)
    body = make_client(llm).post("/api/mission", json=REQ).json()
    assert body["source"] == "gemma"
    first = body["mission"]["objectives"][0]
    assert first["fact_ids"] == ["f_csmt_1"] and first["place_id"] is None
    assert "f_csmt_1" in llm.calls[0]  # grounding facts were actually sent


def test_bad_model_output_falls_back_to_curated(make_client):
    llm = FakeLLM({"title": "x"}, LLMError("down"))
    assert make_client(llm).post("/api/mission", json=REQ).json()["source"] == "curated"


def test_unknown_area_and_city_are_rejected(make_client):
    c = make_client()
    assert c.post("/api/mission", json={**REQ, "area": "Narnia"}).status_code == 422
    assert c.post("/api/mission", json={**REQ, "city": "atlantis"}).status_code == 404
    assert c.post("/api/mission", json={**REQ, "duration_minutes": 7}).status_code == 422


def test_full_session_without_model(make_client):
    c = make_client()
    sid = c.post("/api/mission", json=REQ).json()["session_id"]
    obs = c.post("/api/observation", json={
        "session_id": sid, "text": "Carved faces above the arches",
        "question": "Why are there so many carved faces on this station building?",
    })
    assert obs.status_code == 200 and obs.json()["id"]
    c.post("/api/observation", json={"session_id": sid, "text": "A pigeon on a lamp"})
    j = c.post("/api/reflection", json={"session_id": sid}).json()
    assert j["source"] == "template"
    assert j["journal"]["observation_count"] == 2
    assert j["journal"]["minutes"] >= 1


def test_reflection_with_no_observations_is_still_kind(make_client):
    c = make_client()
    sid = c.post("/api/mission", json=REQ).json()["session_id"]
    j = c.post("/api/reflection", json={"session_id": sid}).json()["journal"]
    assert j["observation_count"] == 0 and "counts" in j["story"]


def test_observation_explanation_and_template_journal(make_client):
    llm = FakeLLM(
        GOOD_MISSION,  # consumed by the mission call
        {"explanation": "Stevens mixed Gothic and Indian motifs.", "fact_ids": ["f_csmt_2", "zzz"]},
        {"title": "A Gothic morning", "story": "You looked up.", "discoveries": ["faces"]},
    )
    c = make_client(llm)
    sid = c.post("/api/mission", json=REQ).json()["session_id"]
    obs = c.post("/api/observation", json={
        "session_id": sid, "text": "carved faces", "question": "Why carved faces on the station?",
    }).json()
    assert obs["explanation"].startswith("Stevens") and obs["fact_ids"] == ["f_csmt_2"]

    j = c.post("/api/reflection", json={"session_id": sid}).json()
    assert j["source"] == "template"
    assert j["journal"]["observation_count"] == 1
    assert "carved faces" in j["journal"]["story"]
    assert j["journal"]["discoveries"] == ["carved faces"]


def test_unknown_session_is_404(make_client):
    c = make_client()
    assert c.post("/api/reflection", json={"session_id": "nope"}).status_code == 404
    assert c.post("/api/observation", json={"session_id": "nope", "text": "hi"}).status_code == 404

def test_unmatched_question_gets_offline_fallback(make_client):
    c = make_client()
    sid = c.post("/api/mission", json=REQ).json()["session_id"]

    response = c.post(
        "/api/observation",
        json={
            "session_id": sid,
            "text": "I saw a parrot",
            "question": "Can all parrots speak?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["question"] == "Can all parrots speak?"
    assert body["explanation"] is not None
    assert "don't have enough information" in body["explanation"]