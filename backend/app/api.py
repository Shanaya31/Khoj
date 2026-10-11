"""HTTP API. Thin: validation in, services out."""

import sqlite3
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Path as PathParam

from . import services
from .db import connect
from .schemas import (
    MissionRequest,
    MissionResponse,
    ObservationRequest,
    ObservationResponse,
    ReflectionRequest,
    ReflectionResponse,
)

router = APIRouter(prefix="/api")


def get_conn(request: Request) -> Iterator[sqlite3.Connection]:
    conn = connect(request.app.state.settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


def _session(conn: sqlite3.Connection, session_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Unknown session. Start a new mission.")
    return row


@router.get("/health")
def health(request: Request):
    s, llm = request.app.state.settings, request.app.state.llm
    return {
        "status": "ok",
        "llm_mode": s.llm_mode,
        "model": s.model if llm else None,
        "llm_reachable": llm.ping() if llm else None,
        "cities": sorted(request.app.state.packs),
    }


@router.get("/cities")
def cities(request: Request):
    return [p.meta for p in request.app.state.packs.values()]


@router.get("/city-pack/{city}")
def city_pack(request: Request, city: str = PathParam(pattern=r"^[a-z0-9_-]{1,40}$")):
    pack = request.app.state.packs.get(city)
    if pack is None:
        raise HTTPException(404, f"No city pack called {city!r}.")
    return pack


@router.post("/mission", response_model=MissionResponse)
def mission(req: MissionRequest, request: Request, conn: sqlite3.Connection = Depends(get_conn)):
    pack = request.app.state.packs.get(req.city)
    if pack is None:
        raise HTTPException(404, f"No city pack called {req.city!r}.")
    if req.area is not None and req.area not in pack.meta.areas:
        raise HTTPException(422, f"Unknown area. Choose one of: {', '.join(pack.meta.areas)}.")
    return services.create_session(conn, request.app.state.llm, req)


@router.post("/observation", response_model=ObservationResponse)
def observation(req: ObservationRequest, request: Request,
                conn: sqlite3.Connection = Depends(get_conn)):
    session = _session(conn, req.session_id)
    return services.add_observation(conn, request.app.state.llm, session, req)


@router.post("/reflection", response_model=ReflectionResponse)
def reflection(req: ReflectionRequest, request: Request,
               conn: sqlite3.Connection = Depends(get_conn)):
    session = _session(conn, req.session_id)
    return services.reflect(conn, request.app.state.llm, session)
