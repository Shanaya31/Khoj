# Architecture

```text
React + Vite (frontend/)
   |  /api              localStorage: cached city pack + on-device fallback
   v
FastAPI (backend/app)
   |-- api.py        thin routes
   |-- services.py   mission / observation / reflection, validation + fallbacks
   |-- retrieval.py  tag + word-overlap search over SQLite rows
   |-- llm.py        OllamaLLM (Gemma) behind a 2-method interface
   |-- db.py         SQLite: places, facts, missions, sessions, observations
   `-- city_pack.py  JSON pack loader + validator
data/cities/<city>/   the contribution surface
```

## Grounding
1. Retrieve facts and places for the area and interest.
2. Send them to Gemma with ids; ask for JSON only.
3. Validate with pydantic; retry once.
4. Drop any `fact_id` / `place_id` not in the pack.
5. On any failure, serve a hand-written mission from the pack.

## Offline behavior
| Capability | Online | Offline |
| --- | --- | --- |
| Download city pack | yes | no |
| Mission | server (Gemma or curated) | built on-device from cached pack (curated) |
| Observation | saved on server, optional explanation | saved on device, no explanation |
| Journal | server (Gemma or template) | template on-device |

Offline *Gemma* in the browser is not implemented; it is the first open validation item.
