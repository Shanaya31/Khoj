"""Model access. One tiny interface so Gemma can be swapped for any open model."""

import json
from typing import Protocol

import httpx


class LLMError(Exception):
    """The model was unreachable or returned something unusable."""


class LLM(Protocol):
    def generate_json(self, system: str, user: str) -> dict: ...
    def ping(self) -> bool: ...


def parse_json_object(text: str) -> dict:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise LLMError("no JSON object in model output") from None
        try:
            obj = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMError(f"invalid JSON from model: {exc}") from exc
    if not isinstance(obj, dict):
        raise LLMError("model output is not a JSON object")
    return obj


class OllamaLLM:
    """Local inference through Ollama's /api/chat (e.g. Gemma)."""

    def __init__(self, host: str, model: str, timeout_s: float = 90.0):
        self.host, self.model, self.timeout_s = host, model, timeout_s

    def generate_json(self, system: str, user: str) -> dict:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.7},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            resp = httpx.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout_s)
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise LLMError(f"ollama request failed: {exc}") from exc
        return parse_json_object(content)

    def ping(self) -> bool:
        try:
            return httpx.get(f"{self.host}/api/tags", timeout=2.0).status_code == 200
        except httpx.HTTPError:
            return False
