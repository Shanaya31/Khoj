# Khoj (खोज)

> *Don't follow the map. Follow your curiosity.*

Khoj is an open-source, offline-first AI exploration companion for discovering the cities
around you. Starting with Mumbai, it uses open-weight Gemma to generate curiosity-driven
exploration missions, help you interpret what you find, and turn your observations into a
personal field journal. Built for the Hacktoberfest 2026 Open-Source AI Challenge, Week 1: *Touch Grass*.

Khoj doesn't tell you where to go. It gives you reasons to look around.

**Flow:** choose time and interest, get a mission, go outside, record what you notice, get a journal.

## Run it locally

Requirements: Python 3.11+, Node 20+, [Ollama](https://ollama.com).

```bash
make setup                      # Python + npm dependencies
ollama pull gemma3:4b           # or any Gemma tag; set KHOJ_MODEL
python scripts/gemma_poc.py     # milestone 1: does Gemma produce a valid Mumbai mission?
make backend                    # http://localhost:8000
make frontend                   # http://localhost:5173 (proxies /api)
make test
```

No Ollama? Set `KHOJ_LLM_MODE=off`. Khoj then serves hand-written missions and templated
journals from the city pack. The model is an enhancement, never a requirement.

## How it works

- `data/cities/<city>/`: the **city pack**, plain JSON that anyone can contribute to.
- `backend/`: FastAPI + SQLite. Retrieves facts from the pack and asks Gemma for structured
  JSON. Output is validated; invented citations are dropped; failures fall back to curated content.
- `frontend/`: React + Vite + Tailwind. Caches the city pack on the device and can build a
  mission locally with no server.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/SPEC.md](docs/SPEC.md).

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Server and model status |
| GET | `/api/cities` | Available city packs |
| GET | `/api/city-pack/{city}` | Download a pack for offline use |
| POST | `/api/mission` | Create a session and mission |
| POST | `/api/observation` | Save an observation, optional question |
| POST | `/api/reflection` | Finish the session, get the journal |

## Honest status

- Mumbai facts are seed data marked `verified: false`; coordinates are approximate.
- A hosted (Render) build has no Ollama, so it runs with `KHOJ_LLM_MODE=off`. Running Gemma
  on an end user's own device from the browser is **not validated yet** (docs/DECISIONS.md).
- Photo observations, map and voice are not built (see FUTURE.md).

## Contributing

Add a city or fix a fact: see [CONTRIBUTING.md](CONTRIBUTING.md). MIT licensed.
