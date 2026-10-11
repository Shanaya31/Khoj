# Khoj spec (condensed single source of truth)

**Challenge:** Hacktoberfest Open-Source AI Challenge, Week 1: *Touch Grass*. **Deadline:** October 11, 2026.
**Owner:** Shanaya Carvalho. **Primary city:** Mumbai.

> Khoj is an open-source, offline-first AI exploration companion that gives people
> curiosity-driven missions to discover the city around them, starting with Mumbai.
> Khoj doesn't tell you where to go. It gives you reasons to look around.

## North star
Does this help someone put their phone down and discover something around them? If not, it isn't Khoj.

## Core loop
Choose -> Explore -> Discover -> Reflect.
Setup (time, interest, area) -> mission -> city pack cached -> go outside -> observations (text, location, optional question) -> journal.
The screen should matter less once exploration begins.

## MVP features
1. Exploration setup: 20 / 45 / 90 / 120+ minutes; history, architecture, nature, art, local life, hidden details, surprise.
2. AI mission generation: Gemma gets location, time, interest and retrieved city knowledge; returns structured JSON. **Must not invent historical facts.**
3. Offline city pack: places, facts, neighborhoods, prompts, missions. No internet for the core flow after download.
4. Observation mode: text, location, optional question; concise grounded explanation where possible.
5. Exploration journal: end-of-session summary and story.

## Not in MVP
Maps replacement, navigation, bookings, social, accounts, multiplayer, recommenders, multi-agent systems,
worldwide data, fine-tuning, blockchain, many AI APIs, complex cloud.

## Rules
1. Working > impressive.
2. No technology without a job.
3. Offline-first is a product requirement. Test with connectivity off; label online enhancements.
4. The user spends less time looking at Khoj than exploring Mumbai.
5. No scope creep before Oct 11. New ideas go to FUTURE.md.

## Stack
Gemma via Ollama; Python + FastAPI; SQLite; React + Vite + Tailwind; Leaflet/OSM (nice-to-have);
Render; GitHub Actions. Optional, only with a job: FAISS, sentence-transformers, Docker, Sentry, ElevenLabs.

## Schedule
| Day | Goal |
| --- | --- |
| Oct 6 | Foundation: scaffold, Gemma/Ollama proof of concept, Mumbai seed data |
| Oct 7 | AI + backend: schema, SQLite, mission generation, prompts, API tests |
| Oct 8 | Frontend: setup, mission, observation, session screens |
| Oct 9 | Offline + end-to-end: test no internet, slow internet, bad AI output, empty sessions |
| Oct 10 | Deploy + polish: Render, CI, README, screenshots, demo video, **take Khoj outside in Mumbai** |
| Oct 11 | Submit. Final fixes, verify repo/deploy/demo, write DEV article |

## Must-have checklist
- [x] Repo scaffold  - [x] FastAPI backend  - [x] Mission generation (with fallback)  - [x] Mumbai pack (seed)
- [x] Observation recording  - [x] Journal  - [x] Tests  - [x] README
- [ ] Gemma validated locally  - [ ] Offline flow tested with network off  - [ ] Real outdoor test
- [ ] Demo  - [ ] DEV article  - [ ] Submission

## Nice to have
Map, FAISS, Docker (files included, untested), Render deploy, Sentry, voice, image understanding.

## Demo target
Open Khoj, choose Mumbai, 60 minutes + Surprise me, get a Gemma mission, keep going when the
connection drops, record a few observations, get a journal; all on public GitHub.
