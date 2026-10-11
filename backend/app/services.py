"""Mission generation, observation explanation and reflection.

Every Gemma call is wrapped: invalid or unreachable output falls back to curated or
template content, so the core flow never depends on the model being up.
"""

import json
import random
import re
import sqlite3
import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ValidationError

from . import prompts
from .llm import LLM, LLMError
from .retrieval import find_facts, find_places
from .schemas import (
    Journal,
    Mission,
    MissionRequest,
    MissionResponse,
    Objective,
    ObservationRequest,
    ObservationResponse,
    ReflectionResponse,
)

MODEL_ATTEMPTS = 2


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _objective_count(duration: int) -> int:
    return {20: 3, 45: 4, 90: 5, 120: 6}[duration]


def _ids(conn: sqlite3.Connection, table: str, city: str) -> set[str]:
    return {
        r["id"]
        for r in conn.execute(
            f"SELECT id FROM {table} WHERE city = ?", (city,)
        )
    }


# --------------------------------------------------------------------------- missions

def _sanitize(
    mission: Mission,
    fact_ids: set[str],
    place_ids: set[str],
    allowed_fact_ids: set[str] | None = None,
    allowed_place_ids: set[str] | None = None,
) -> Mission:
    """Validate citations and remove citation IDs leaked into visible prose.

    Gemma is instructed to keep IDs inside structured fields, but local models can
    occasionally leak them into objective text. Valid leaked fact IDs are recovered
    into fact_ids, while all citation tokens are removed from visible text.
    """

    allowed_fact_ids = allowed_fact_ids or fact_ids
    allowed_place_ids = allowed_place_ids or place_ids

    for obj in mission.objectives:
        # Keep only facts that were actually supplied to this generation request.
        obj.fact_ids = [
            fact_id
            for fact_id in obj.fact_ids
            if fact_id in allowed_fact_ids and fact_id in fact_ids
        ]

        # Recover leaked fact IDs such as "[f_flora]" from visible text.
        leaked_ids = re.findall(r"\[([^\[\]]+)\]", obj.text)

        for leaked_id in leaked_ids:
            if leaked_id in allowed_fact_ids and leaked_id in fact_ids:
                if leaked_id not in obj.fact_ids:
                    obj.fact_ids.append(leaked_id)

            # Remove known citation IDs from visible prose.
            if leaked_id in allowed_fact_ids or leaked_id in allowed_place_ids:
                obj.text = obj.text.replace(f"[{leaked_id}]", "")

        obj.text = " ".join(obj.text.split()).strip()

        # Only allow a place that was actually supplied for this generation.
        if obj.place_id not in allowed_place_ids:
            obj.place_id = None

    return mission


def _curated_mission(conn: sqlite3.Connection, req: MissionRequest) -> Mission:
    rows = conn.execute(
        "SELECT * FROM missions WHERE city = ?", (req.city,)
    ).fetchall()

    if not rows:
        raise ValueError(f"no missions in pack for {req.city}")

    pool = [
        r
        for r in rows
        if req.interest == "surprise" or r["interest"] == req.interest
    ]
    pool = pool or list(rows)

    best = min(
        abs(r["duration_minutes"] - req.duration_minutes)
        for r in pool
    )

    row = random.choice(
        [
            r
            for r in pool
            if abs(r["duration_minutes"] - req.duration_minutes) == best
        ]
    )

    return Mission(
        title=row["title"],
        intro=row["intro"] or "",
        objectives=[
            Objective(text=t)
            for t in json.loads(row["objectives"])
        ],
        closing="Put your phone away and start exploring.",
    )


def _format_facts(facts: list[dict]) -> str:
    return "\n".join(
        f"[{f['id']}] {f['text']}"
        for f in facts
    ) or "(none)"


def generate_mission(
    conn: sqlite3.Connection,
    llm: LLM | None,
    req: MissionRequest,
) -> tuple[Mission, str]:

    if llm is not None:
        facts = find_facts(
            conn,
            req.city,
            area=req.area,
            interest=req.interest,
            k=8,
        )

        places = find_places(
            conn,
            req.city,
            area=req.area,
            interest=req.interest,
            k=6,
        )

        user = prompts.MISSION_USER.format(
            city=req.city,
            area=req.area or "anywhere in the city",
            duration=req.duration_minutes,
            interest=req.interest.replace("_", " "),
            facts=_format_facts(facts),
            places="\n".join(
                f"[{p['id']}] {p['name']} ({p['area']}): {p['summary']}"
                for p in places
            ) or "(none)",
            n_objectives=_objective_count(req.duration_minutes),
        )

        # Only citations from the retrieved context should be accepted.
        retrieved_fact_ids = {f["id"] for f in facts}
        retrieved_place_ids = {p["id"] for p in places}

        for _ in range(MODEL_ATTEMPTS):
            try:
                raw = llm.generate_json(
                    prompts.MISSION_SYSTEM,
                    user,
                )

                mission = Mission.model_validate(raw)

                all_fact_ids = _ids(
                    conn,
                    "facts",
                    req.city,
                )
                all_place_ids = _ids(
                    conn,
                    "places",
                    req.city,
                )

                mission = _sanitize(
                    mission,
                    all_fact_ids,
                    all_place_ids,
                    allowed_fact_ids=retrieved_fact_ids,
                    allowed_place_ids=retrieved_place_ids,
                )

                return mission, "gemma"

            except (LLMError, ValidationError):
                continue

    return _curated_mission(conn, req), "curated"


def create_session(
    conn: sqlite3.Connection,
    llm: LLM | None,
    req: MissionRequest,
) -> MissionResponse:

    mission, source = generate_mission(conn, llm, req)

    session_id = uuid.uuid4().hex[:12]

    conn.execute(
        "INSERT INTO sessions (id, city, area, interest, duration_minutes, mission, "
        "mission_source, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (
            session_id,
            req.city,
            req.area,
            req.interest,
            req.duration_minutes,
            mission.model_dump_json(),
            source,
            now_iso(),
        ),
    )

    conn.commit()

    return MissionResponse(
        session_id=session_id,
        city=req.city,
        area=req.area,
        duration_minutes=req.duration_minutes,
        interest=req.interest,
        mission=mission,
        source=source,
    )


# ------------------------------------------------------------------------ observations

class _Explanation(BaseModel):
    explanation: str
    fact_ids: list[str] = []


def add_observation(
    conn: sqlite3.Connection,
    llm: LLM | None,
    session: sqlite3.Row,
    req: ObservationRequest,
) -> ObservationResponse:

    explanation, used = None, []

    if req.question:
        query = f"{req.text} {req.question}"

        facts = find_facts(
            conn,
            session["city"],
            area=session["area"],
            query=query,
            k=3,
            min_overlap=1,
        )

        if llm is not None:
            user = prompts.OBSERVATION_USER.format(
                city=session["city"],
                area=session["area"] or "unknown",
                text=req.text,
                question=req.question,
                facts=_format_facts(facts),
            )

            try:
                out = _Explanation.model_validate(
                    llm.generate_json(
                        prompts.OBSERVATION_SYSTEM,
                        user,
                    )
                )

                valid = _ids(
                    conn,
                    "facts",
                    session["city"],
                )

                explanation = out.explanation
                used = [
                    f
                    for f in out.fact_ids
                    if f in valid
                ]

            except (LLMError, ValidationError):
                pass

        if explanation is None:
            if facts:
                explanation = (
                    f"From the local city pack: {facts[0]['text']}"
                )
                used = [facts[0]["id"]]
            else:
                explanation = (
                    "I don't have enough information in this city's offline "
                    "guide to answer that confidently. Keep observing, or "
                    "look for a local information sign to learn more."
                )

    obs_id, created = uuid.uuid4().hex[:12], now_iso()

    conn.execute(
        "INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?)",
        (
            obs_id,
            session["id"],
            req.text,
            req.question,
            req.lat,
            req.lon,
            explanation,
            json.dumps(used),
            created,
        ),
    )

    conn.commit()

    return ObservationResponse(
        id=obs_id,
        session_id=session["id"],
        text=req.text,
        question=req.question,
        explanation=explanation,
        fact_ids=used,
        created_at=created,
    )


# ------------------------------------------------------------------------- reflection

class _JournalDraft(BaseModel):
    title: str
    story: str
    discoveries: list[str] = []


def _template_journal(
    title: str,
    minutes: int,
    where: str,
    obs: list[sqlite3.Row],
) -> _JournalDraft:
    if not obs:
        story = (
            f"You spent {minutes} minute{'s' if minutes != 1 else ''} "
            f"around {where} with your phone mostly in your pocket. "
            "You didn't write anything down this time, and that counts too."
        )

        return _JournalDraft(
            title=title,
            story=story,
            discoveries=[],
        )

    discoveries = []
    seen = set()

    for observation in obs:
        text = " ".join(observation["text"].split()).strip()
        text = text.rstrip(".!? ")

        if text and text.casefold() not in seen:
            discoveries.append(text)
            seen.add(text.casefold())

        if len(discoveries) == 5:
            break

    count = len(discoveries)

    if count == 1:
        summary = f"One detail stood out to you: {discoveries[0]}."
    elif count == 2:
        summary = (
            f"Two details caught your attention: "
            f"{discoveries[0]} and {discoveries[1]}."
        )
    elif count > 2:
        summary = (
            f"Your exploration brought several details into focus. "
            f"You noticed {discoveries[0].lower()}, alongside other details "
            "that made this place worth exploring."
        )
    else:
        summary = (
            "You took time to explore, even though you didn't record "
            "a specific observation."
        )

    story = (
        f"You spent {minutes} minute{'s' if minutes != 1 else ''} "
        f"around {where}. {summary}"
    )

    return _JournalDraft(
        title=title,
        story=story,
        discoveries=discoveries,
    )

def reflect(
    conn: sqlite3.Connection,
    llm: LLM | None,
    session: sqlite3.Row,
) -> ReflectionResponse:
    """Build a journal from saved observations without inventing discoveries."""

    mission = Mission.model_validate_json(session["mission"])

    obs = conn.execute(
        "SELECT * FROM observations WHERE session_id = ? ORDER BY created_at",
        (session["id"],),
    ).fetchall()

    started = datetime.fromisoformat(session["created_at"])
    minutes = max(
        1,
        round((datetime.now(UTC) - started).total_seconds() / 60),
    )

    where = session["area"] or session["city"].title()

    # Use the saved observations as the sole source of journal discoveries.
    # Do not ask Gemma to turn mission objectives into claimed sightings.
    draft = _template_journal(
        mission.title,
        minutes,
        where,
        obs,
    )

    journal = Journal(
        title=draft.title,
        minutes=minutes,
        observation_count=len(obs),
        discoveries=draft.discoveries[:5],
        story=draft.story,
    )

    conn.execute(
        "UPDATE sessions SET finished_at = ?, journal = ? WHERE id = ?",
        (
            now_iso(),
            journal.model_dump_json(),
            session["id"],
        ),
    )

    conn.commit()

    return ReflectionResponse(
        session_id=session["id"],
        journal=journal,
        source="template",
    )