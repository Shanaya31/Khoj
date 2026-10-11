.PHONY: setup backend frontend test lint poc

setup:
	pip install -r backend/requirements-dev.txt
	cd frontend && npm install

backend:
	uvicorn app.main:app --reload --app-dir backend

frontend:
	cd frontend && npm run dev

test:
	python -m pytest -q

lint:
	ruff check backend tests scripts

poc:
	python scripts/gemma_poc.py
