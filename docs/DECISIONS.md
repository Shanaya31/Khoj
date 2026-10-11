# Decisions and open validation

## Open: how does Gemma run when the user is offline?
Ollama runs on a laptop, not in a phone browser. A Render-hosted web build cannot run Gemma
for the user and has no Ollama, so it uses `KHOJ_LLM_MODE=off`. **Do not claim otherwise**
until one of these is tested end to end:
1. User runs the stack locally (docker-compose) and opens it on a laptop. Works today.
2. Phone on the same network as a laptop running Ollama.
3. In-browser or on-device Gemma runtime. Unvalidated; may not fit the Oct 11 deadline.

## Decided
- **Keyword retrieval, not FAISS.** 20 facts per city do not need vectors. Revisit above ~500 facts.
- **Curated fallback everywhere.** Bad or missing model output never blocks a session.
- **Sessions live in SQLite; the pack is re-seeded on startup** so editing JSON is enough.
- **No accounts.** A session id is the only identity.
- **Model name is config** (`KHOJ_MODEL`) so any compatible open model can replace Gemma.
