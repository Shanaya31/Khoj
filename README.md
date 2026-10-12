# Khoj (खोज)

> *Don't follow the map. Follow your curiosity.*

**Khoj** is an open-source, offline-first AI exploration companion for discovering the city around you. Starting with Mumbai, it offers curiosity-driven missions, lets you record what you notice, and helps you turn those observations into a personal field journal.

Built for the **Hacktoberfest 2026 Open-Source AI Challenge, Week 1: Touch Grass**.

**[Live Demo](https://khoj-37vp.onrender.com/)** · **[Source Code](https://github.com/Shanaya31/Khoj)**

Khoj doesn't tell you where to go. It gives you reasons to look around.

## Table of Contents

- [See Khoj in Action](#see-khoj-in-action)
- [How It Works](#how-it-works)
- [Offline-First Design](#offline-first-design)
- [AI and Fallback Behavior](#ai-and-fallback-behavior)
- [Run Locally](#run-locally)
- [Technical Architecture](#technical-architecture)
- [API Reference](#api-reference)
- [Current Limitations](#current-limitations)
- [Contributing](#contributing)
- [License](#license)

## See Khoj in Action

The following screenshots show the application and its exploration experience.

![Khoj application](Screenshots/Screenshot.png)

![Khoj exploration screen](Screenshots/Screenshot%20%281%29.png)

![Khoj mission experience](Screenshots/Screenshot%20%282%29.png)

![Khoj exploration interface](Screenshots/Screenshot%20%283%29.png)

![Khoj mission in progress](Screenshots/Screenshot%20%284%29.png)

![Khoj observation experience](Screenshots/Screenshot%20%285%29.png)

![Khoj field journal](Screenshots/Screenshot%20%286%29.png)

![Khoj offline experience](Screenshots/Screenshot%20%287%29.png)

## How It Works

1. **Choose:** Select an exploration duration and an interest.
2. **Discover:** Receive a mission with prompts that encourage curiosity about your surroundings.
3. **Explore:** Head outside and record observations and notes.
4. **Reflect:** Finish your session and create a personal field journal grounded in your saved observations.

## Offline-First Design

Khoj is designed to keep exploration and progress available when internet connectivity is unreliable.

- **Cached app shell:** A service worker caches the application shell and static assets after an online visit.
- **Session persistence:** The active session and screen state are saved locally, allowing progress to survive a page refresh.
- **Local observations:** Observations are stored in browser storage.
- **Downloaded city packs:** City data can be cached on the device and used to build curated missions locally.
- **Fallback behavior:** The basic exploration experience does not require a running AI model.

### Offline Testing

The deployed application was tested using Chrome DevTools' Offline network setting. The tested mission-to-journal flow completed, and refreshing the page did not lose the active session or saved observations.

For the first offline session, open the app while online so the application assets and city pack can be cached.

Offline availability depends on previously cached assets and city data. Network-dependent features may still be unavailable without connectivity.

## AI and Fallback Behavior

Khoj supports **Gemma through Ollama** for local AI-assisted mission generation and related features when the model is available.

The hosted Render deployment runs with `KHOJ_LLM_MODE=off`. It uses curated missions and fallback behavior rather than hosting a Gemma model.

The model is an enhancement, never a requirement for the basic exploration experience.

## Run Locally

### Requirements

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/) for local Gemma support
- Git

### Setup

Clone the repository:

```bash
git clone https://github.com/Shanaya31/Khoj.git
cd Khoj

Install dependencies:

```bash
make setup
```

Download Gemma:

```bash
ollama pull gemma3:4b
```

Run the Gemma proof of concept:

```bash
python scripts/gemma_poc.py
```

Start the backend:

```bash
make backend
```

The FastAPI backend runs at `http://localhost:8000`.

In a separate terminal, start the frontend:

```bash
make frontend
```

The Vite frontend runs at `http://localhost:5173` and proxies API requests to the backend.

Run the tests:

```bash
make test
```

### Running Without Ollama

Set the environment variable `KHOJ_LLM_MODE=off` to disable local model integration. Khoj can then use curated missions and fallback behavior from the city pack.

## Technical Architecture

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | React, Vite, Tailwind CSS | Exploration interface and user experience |
| Backend | Python, FastAPI | API endpoints and mission workflows |
| Storage | SQLite and browser storage | Session data and locally saved observations |
| AI | Gemma 3 via Ollama | Optional local AI-assisted generation |
| Offline support | Service worker, local storage, IndexedDB | Cached assets, session persistence, and local observations |
| Deployment | Docker, Render | Hosted application |

### Project Structure

```text
Khoj/
├── backend/          # FastAPI backend
├── frontend/         # React application
│   ├── public/       # Static assets and service worker
│   └── src/          # UI, local storage, and offline logic
├── data/
│   └── cities/       # City packs and factual data
├── docs/             # Architecture and design documents
├── scripts/          # AI proof-of-concept scripts
├── tests/            # Automated tests
├── Dockerfile
├── render.yaml
├── Makefile
└── README.md
```

City packs are plain JSON, making it possible for contributors to add cities and improve existing data.

For additional details, see:

- [Architecture](docs/ARCHITECTURE.md)
- [Specification](docs/SPEC.md)
- [Technical Decisions](docs/DECISIONS.md)
- [Contributing Guide](CONTRIBUTING.md)

## API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check server and model status |
| `GET` | `/api/cities` | List available city packs |
| `GET` | `/api/city-pack/{city}` | Retrieve a city's exploration data |
| `POST` | `/api/mission` | Create an exploration session and mission |
| `POST` | `/api/observation` | Submit an observation and optional question |
| `POST` | `/api/reflection` | Finish a session and generate a journal |

## Current Limitations

- Mumbai facts are seed data marked `verified: false`; coordinates are approximate.
- The hosted Render deployment does not run Ollama or host a Gemma model.
- Running Gemma directly on an end user's device from the browser has not been validated.
- Offline functionality depends on previously cached assets and city data.
- Network-dependent features are not guaranteed to work offline.
- Dedicated map and voice features are not implemented.

## Contributing

Contributions are welcome! You can help by:

- Adding a city pack.
- Improving factual accuracy and sourcing.
- Fixing bugs or improving offline behavior.
- Improving accessibility and the user experience.
- Adding automated tests and documentation.

Please read the [Contributing Guide](CONTRIBUTING.md) before submitting changes.

## License

Khoj is released under the [MIT License](LICENSE).

*Built with curiosity, for curious explorers.*
