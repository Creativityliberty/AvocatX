# Plan de Restructuration — AvocatX / DEFENSEUR-IA

Date: 2025-08-08
Auteur: Cascade (audit + proposition de refonte)

## 1) Objectifs
- Sécuriser la configuration (zéro secret committé, `.env.example` documentés)
- Clarifier la structure monorepo (backend / frontend / docs / infra)
- Normaliser la configuration du backend (Pydantic Settings, logging, migrations)
- Standardiser les conventions frontend (services, hooks, pages, ESLint/Prettier)
- Professionnaliser le cycle de vie (pré-commit, CI/CD, tests, qualité)
- Faciliter le déploiement Docker (images dédiées, healthchecks, variables)

## 2) État actuel (extrait de l'audit)
- Secrets présents dans `backend/.env` (rotation urgente)
- Entrypoint backend parfois référencé comme `main:app` au lieu de `src.defenseur_ia.main:app`
- Compose/Dockerfiles clarifiés et séparés, mais besoin d’harmonisation des variables
- Frontend dépend de `REACT_APP_API_URL` avec fallback local — uniformisé vers 8000
- Documentation morcelée (`PROJECT_RECAP.md` vs `docs/`)

## 3) Structure cible (monorepo)
```
/ (monorepo)
├─ backend/
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  ├─ poetry.lock
│  ├─ .env.example
│  ├─ src/defenseur_ia/
│  │  ├─ api/            # routers versionnés (api/v1)
│  │  ├─ core/           # pipeline, websocket, utils
│  │  ├─ services/       # storage, providers, adapters
│  │  ├─ agents/         # AI agents
│  │  ├─ models/         # pydantic/ORM models
│  │  ├─ config/         # settings (Pydantic), logging config
│  │  ├─ orchestrator/   # flows orchestration
│  │  ├─ monitoring/     # metrics, traces, health
│  │  └─ main.py         # FastAPI app
│  ├─ migrations/        # Alembic
│  └─ tests/             # unit, integration, e2e
├─ frontend/
│  ├─ Dockerfile
│  ├─ .env.example
│  └─ src/
│     ├─ services/
│     ├─ hooks/
│     ├─ components/
│     ├─ pages/
│     ├─ store/ (option)
│     └─ assets/
├─ docs/
│  ├─ PROJECT_AUDIT.md
│  ├─ RESTRUCTURE_PLAN.md
│  ├─ OVERVIEW_ARCHITECTURE.md (ou existant)
│  └─ DEVELOPMENT.md (onboarding dev)
├─ docker-compose.yml
├─ BACKEND_GUIDE.md
├─ Makefile (qualité/dev/ops)
└─ README.md
```

## 4) Backend — changements proposés
- Configuration
  - Introduire `config/settings.py` (Pydantic BaseSettings) pour charger `.env` (Postgres, Redis, API Keys)
  - Centraliser les constantes et URLs (ex: uploads dir) et supprimer les valeurs hardcodées
  - Ajouter `logging.ini` + configuration JSON (prod) + niveaux par module
- API & routes
  - Uniformiser les préfixes sous `/api/v1` (éviter le mélange `/api` et `/api/v1`)
  - Séparer routers par domaine: `cases`, `pipeline`, `agents`, `stats`, `upload`
  - Définir `response_model` et schémas d’erreurs cohérents (Pydantic)
- Persistance & migrations
  - Introduire Alembic pour PostgreSQL, versionner le schéma, script d’init
  - Scripts de maintenance (backup/restore) dans `backend/scripts/`
- Qualité
  - Activer `black`, `isort`, `flake8`, `mypy` (déjà partiel via pyproject)
  - Tests `pytest`: `tests/unit`, `tests/integration`, `tests/e2e`
- Observabilité
  - `/health` enrichi + métriques Prometheus (ex: `prometheus-fastapi-instrumentator`)
  - Sentry (optionnel) pour exceptions en prod
- WebSocket
  - Heartbeat/ping, reconnexion côté client, gestion d’autorisations (si besoin)

## 5) Frontend — changements proposés
- Configuration
  - Standardiser `REACT_APP_API_URL` (env local: `http://localhost:8000`)
  - Ajouter `.env.example` (fait) et documentation d’usage
- Architecture
  - Dossier `src/` structuré: `services/`, `hooks/`, `components/`, `pages/`, `store/`
  - Option: migration progressive vers TypeScript
- Qualité
  - ESLint + Prettier (config + scripts), `.editorconfig`
  - Tests: React Testing Library/Jest pour composants clés
- Build & runtime
  - Nginx SPA fallback (déjà géré) + compression Gzip/Brotli (option)

## 6) Tooling & DevEx
- Makefile ou scripts npm
  - `make install`, `make dev`, `make test`, `make lint`, `make fmt`, `make docker-up`, `make docker-down`
- Pré-commit
  - Hooks: black, isort, flake8, mypy, prettier, eslint
- Versions
  - `.python-version`/`.tool-versions` (asdf) ou `.nvmrc` pour Node

## 7) CI/CD (GitHub Actions)
- Workflows
  - `lint-and-test`: backend (pytest, mypy, flake8), frontend (eslint, tests)
  - `build-and-push`: build images Docker backend/front, push vers GHCR/registry
  - `release`: sur tag, build images versionnées + changelog
- Secrets
  - Déplacer toutes les clés vers GitHub Secrets/1Password/Doppler

## 8) Docker & Compose
- Services
  - `api` (backend), `web` (frontend), `postgres`, `redis`
- Healthchecks explicites + `depends_on.condition: service_healthy`
- Volumes persistants pour `postgres`, `uploads`
- Variables
  - Centralisation dans `.env` racine si pertinent (ports, URLs), tout en gardant `backend/.env` pour secrets locaux

## 9) Documentation
- Consolider dans `docs/` (supprimer ou intégrer `PROJECT_RECAP.md` si redondant)
- Ajouter `DEVELOPMENT.md` (onboarding + commandes) et `DEPLOYMENT.md`
- Mettre à jour `README.md` (stack réelle, quickstart, docker)

## 10) Sécurité
- Retirer le `.env` réel de l’historique Git si poussé (réécriture)
- Rotation immédiate des clés exposées
- Politique de gestion des secrets (vault/secret manager)

## 11) Plan de migration (par étapes)
1. Sécurité: rotation des clés + purge de l’historique si nécessaire
2. Documentation: consolider `docs/`, publier `PROJECT_AUDIT.md` & `RESTRUCTURE_PLAN.md`
3. Config backend: `settings.py`, logging, centralisation des variables
4. Qualité: pré-commit, Makefile, ESLint/Prettier, CI lint+tests
5. Base de données: init Alembic, script d’init, pipelines
6. API: uniformiser préfixes `/api/v1` et schémas de réponse
7. Tests: coverage minimal (unit/integration), e2e ciblés
8. Observabilité: métriques, traces (optionnel), Sentry (optionnel)

## 12) Checklist
- [ ] Secrets: rotation et suppression de l’historique
- [ ] `docs/` consolidé; README mis à jour
- [ ] `backend/config/settings.py` + logging config
- [ ] Alembic initialisé et migrations créées
- [ ] Pré-commit + Makefile
- [ ] ESLint/Prettier et tests frontend
- [ ] CI GitHub Actions (lint/test/build)
- [ ] Uniformisation `/api/v1` + schémas Pydantic
- [ ] Observabilité (métriques, healthchecks)

---
Ce plan est conçu pour des itérations courtes (1–2 jours par lot). Merci de valider les priorités (sécurité, config, CI) avant lancement de l’implémentation.
