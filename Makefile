# Makefile for AvocatX / DEFENSEUR-IA
SHELL := /bin/zsh

# Prefer podman-compose if available, fallback to docker-compose
COMPOSE ?= $(shell command -v podman-compose 2>/dev/null || command -v docker-compose 2>/dev/null || echo podman compose)

.PHONY: help
help:
	@echo "Targets:"
	@echo "  install           - Install backend (poetry) and frontend deps"
	@echo "  install-backend   - Poetry install"
	@echo "  install-frontend  - npm ci in frontend"
	@echo "  dev               - Start concurrent backend + frontend (npm scripts)"
	@echo "  docker-up         - Start containers with compose"
	@echo "  docker-down       - Stop containers"
	@echo "  docker-logs       - Tail backend logs"
	@echo "  lint              - Lint backend (flake8, mypy) and frontend (eslint)"
	@echo "  fmt               - Format backend (black, isort) and frontend (prettier)"
	@echo "  test              - Run backend tests"
	@echo "  pre-commit-install- Install and enable pre-commit hooks"

.PHONY: install
install: install-backend install-frontend

.PHONY: install-backend
install-backend:
	cd backend && poetry install

.PHONY: install-frontend
install-frontend:
	cd frontend && npm ci || npm install

.PHONY: dev
dev:
	npm run dev

.PHONY: docker-up
docker-up:
	$(COMPOSE) up -d

.PHONY: docker-down
docker-down:
	$(COMPOSE) down

.PHONY: docker-logs
docker-logs:
	$(COMPOSE) logs -f backend

.PHONY: lint
lint:
	cd backend && poetry run flake8 && poetry run mypy
	cd frontend && npx eslint . || true

.PHONY: fmt
fmt:
	cd backend && poetry run isort . && poetry run black .
	cd frontend && npx prettier -w "src/**/*.{js,jsx,ts,tsx,css,scss,json,md}"

.PHONY: test
test:
	cd backend && poetry run pytest

.PHONY: pre-commit-install
pre-commit-install:
	cd backend && poetry run pre-commit install
