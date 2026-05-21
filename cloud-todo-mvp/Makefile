.PHONY: up down test lint migrate openapi

up:
	docker compose up --build

down:
	docker compose down -v

test:
	cd backend && pytest

lint:
	cd backend && ruff check app tests

migrate:
	cd backend && alembic upgrade head

openapi:
	cd backend && python -c "import json; from app.main import create_app; print(json.dumps(create_app().openapi(), indent=2))" > openapi.json
