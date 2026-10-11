# Single-service image: FastAPI serves the built React app. Used by Render and docker-compose.
FROM node:20-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend backend
COPY data data
COPY --from=web /web/dist frontend/dist
# Hosted default: no model server available, so use curated missions. See docs/DECISIONS.md.
ENV KHOJ_LLM_MODE=off
CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
