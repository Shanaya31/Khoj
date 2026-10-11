"""FastAPI entrypoint.  Run:  uvicorn app.main:app --reload --app-dir backend"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import router
from .city_pack import list_city_dirs, load_city_pack
from .config import Settings, get_settings
from .db import connect, init_db, seed_city
from .llm import LLM, OllamaLLM


def create_app(settings: Settings | None = None, llm: LLM | None = None) -> FastAPI:
    settings = settings or get_settings()
    if llm is None and settings.llm_mode == "ollama":
        llm = OllamaLLM(settings.ollama_host, settings.model, settings.timeout_s)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        packs = {}
        conn = connect(settings.db_path)
        try:
            init_db(conn)
            for city_dir in list_city_dirs(settings.data_dir):
                pack = load_city_pack(city_dir)  # fails loudly on a broken pack
                seed_city(conn, pack)
                packs[pack.meta.city] = pack
        finally:
            conn.close()
        app.state.packs = packs
        yield

    app = FastAPI(title="Khoj", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.llm = llm
    app.state.packs = {}
    app.include_router(router)

    if settings.frontend_dist.is_dir():  # single-service deploys (Render, Docker)
        app.mount("/", StaticFiles(directory=settings.frontend_dist, html=True), name="web")
    return app


app = create_app()
