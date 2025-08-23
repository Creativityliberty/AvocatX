# Projet DEFENSEUR-IA / AvocatX — Audit & Correctifs appliqués

Date: 2025-08-08

## 1) Vue d’ensemble
Monorepo avec:
- backend: Python 3.12 (FastAPI, Uvicorn, Poetry), services Postgres + Redis
- frontend: React (CRA + MUI)
- orchestration: Docker Compose (PostgreSQL, Redis, Backend FastAPI, Frontend Nginx)
- docs: documentation technique et fonctionnelle

## 2) Points relevés
- Secrets exposés dans `backend/.env` (API keys, MongoDB, Légifrance): RISQUE CRITIQUE
- `docker-compose.yml` pointait vers un build root ambigu; `Dockerfile` racine inadapté (pyproject au niveau backend)
- Absence de `.gitignore` global: risque de commit de fichiers sensibles/build
- Scripts de démarrage backend ciblant `main:app` (ambigu) au lieu de `src.defenseur_ia.main:app`
- `README.md` racine inexact (backend Node/Express + MongoDB) vs stack réelle (FastAPI + Postgres/Redis)
- Manque d’exemples `.env.example`

## 3) Correctifs effectués (techniques)
- Ajout `.gitignore` global (Python, Node, Docker, uploads, .env)
- Ajout `backend/Dockerfile` (Poetry + FastAPI) et `frontend/Dockerfile` (build React + Nginx)
- Mise à jour `docker-compose.yml`:
  - backend: `build.context: ./backend`, `env_file: ./backend/.env`, volume `./backend/uploads:/app/uploads`
  - frontend: `build.context: ./frontend`, build arg `REACT_APP_API_URL=http://backend:8000`, ports `3000:80`
- Correction import manquant `from datetime import datetime` dans `backend/main.py`
- Mise à jour `package.json` racine: script `dev:backend` → `uvicorn src.defenseur_ia.main:app`
- Ajout `backend/.env.example` (sans secrets)

## 4) Actions urgentes (sécurité)
- ROTATION IMMÉDIATE des clés exposées: OpenAI, Gemini, Pinecone, Légifrance, MongoDB
- Retirer `backend/.env` de l’historique Git (réécriture de l’historique) si déjà poussé
  - Exemple: `git filter-repo` ou `git filter-branch` (guide à prévoir)
- Utiliser un gestionnaire de secrets (1Password, Doppler, GitHub Actions Secrets) pour CI/CD

## 5) Recommandations d’organisation
- Structure cible
  ```
  / (monorepo)
  ├─ backend/
  │  ├─ Dockerfile
  │  ├─ pyproject.toml
  │  ├─ poetry.lock
  │  ├─ .env.example
  │  ├─ src/defenseur_ia/
  │  │  ├─ api/ core/ services/ agents/ models/ config/ orchestrator/ monitoring/
  │  │  └─ main.py
  │  ├─ tests/
  │  └─ scripts/
  ├─ frontend/
  │  ├─ Dockerfile
  │  ├─ .env.example
  │  └─ src/ ...
  ├─ docs/
  │  ├─ PROJECT_AUDIT.md
  │  ├─ RESTRUCTURE_PLAN.md
  │  └─ overview-architecture.md (existant)
  ├─ docker-compose.yml
  ├─ BACKEND_GUIDE.md (existant)
  ├─ start_project.py (optionnel)
  └─ README.md (mis à jour)
  ```
- Standards
  - Python: black, isort, flake8, mypy (déjà référencés dans `pyproject.toml`)
  - JS: eslint + prettier (à ajouter côté frontend si absent)
  - Hooks: `pre-commit` recommandé

## 6) Prochaines étapes proposées
- [Sécurité] Rotation des secrets + suppression de `backend/.env` de l’historique Git
- [CI/CD] Workflow GitHub Actions: lint + tests + build images Docker
- [Qualité] Ajouter tests backend (pytest) et frontend (React Testing Library)
- [Ops] Ajouter `Makefile` ou scripts npm: `npm run docker:up`, `docker:down`, `lint`, `test`
- [Docs] Compléter `BACKEND_GUIDE.md` (endpoints actuels), ajouter `FRONTEND_GUIDE.md` si besoin

## 7) Comment démarrer (local)
- Dev sans Docker:
  - Backend: `cd backend && poetry install && poetry run uvicorn src.defenseur_ia.main:app --reload`
  - Frontend: `cd frontend && npm install && npm start`
- Docker:
  - `docker-compose up -d` (build auto, front sur http://localhost:3000, API sur http://localhost:8000)

## 8) Risques résiduels
- Fichiers/Docs mentionnant des chemins obsolètes (à harmoniser)
- Double point d’entrée backend (`backend/main.py` et `src/defenseur_ia/main.py`) → garder un seul entrypoint (prévu dans plan)

---
Document maintenable. Ouvrir une issue pour demandes de modifications.
