# Contributing to Khoj

The easiest contribution needs no code and no AI knowledge: **improve or add a city pack.**

## Add a city

```text
data/cities/<city-slug>/
  pack.json                  city slug (must match folder), display name, areas
  places.json                places worth noticing
  history.json               short, checkable facts
  missions.json              hand-written missions (3-6 objectives each)
  observation_prompts.json   gentle nudges shown while exploring
```

Copy `data/cities/mumbai/` and edit. Then run `python -m pytest -q`; the pack validator
catches duplicate ids, unknown areas and dangling `place_id`s.

## Fact rules

- Facts are the **only** material the AI is allowed to use. Keep each to one checkable sentence.
- Add a `source` (UNESCO listing, official site, a book) and set `verified: true` only after you checked it.
- Don't write opinions or "famous for" claims you can't point to.
- Coordinates may be approximate; say so in `pack.json` (`coords_approximate`).

## Code

- `python -m pytest -q` and `ruff check backend tests scripts` must pass.
- No new dependency without a job. Say what problem it solves in the PR.
- Scope check: does it help someone put their phone down and discover something around them?
  If not, it belongs in `FUTURE.md`.
