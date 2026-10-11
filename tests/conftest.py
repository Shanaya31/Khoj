import pytest
from app.config import ROOT, Settings
from app.llm import LLMError
from app.main import create_app
from fastapi.testclient import TestClient


class FakeLLM:
    """Scripted model: pops one response per call. Exceptions are raised."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls: list[str] = []

    def generate_json(self, system: str, user: str) -> dict:
        self.calls.append(user)
        if not self.responses:
            raise LLMError("no scripted response")
        out = self.responses.pop(0)
        if isinstance(out, Exception):
            raise out
        return out

    def ping(self) -> bool:
        return True


@pytest.fixture
def make_client(tmp_path):
    clients = []

    def _make(llm=None):
        settings = Settings(
            data_dir=ROOT / "data",
            db_path=tmp_path / "test.sqlite3",
            llm_mode="off",
            ollama_host="http://localhost:11434",
            model="test",
            timeout_s=1.0,
            frontend_dist=tmp_path / "no-dist",
        )
        client = TestClient(create_app(settings, llm))
        client.__enter__()  # runs lifespan: seeds SQLite from data/cities
        clients.append(client)
        return client

    yield _make
    for c in clients:
        c.__exit__(None, None, None)
