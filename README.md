# DEFENSEUR-IA

Application web pour les avocats.

## Description

DEFENSEUR-IA est une application web moderne conçue pour faciliter la gestion des dossiers et le travail quotidien des avocats.

## Installation

1. Cloner le dépôt
2. Installer les dépendances
3. Configurer l'environnement
4. Lancer l'application

## Technologies utilisées

- Frontend: React.js (CRA, MUI)
- Backend: FastAPI (Python 3.12)
- Base de données: PostgreSQL + Redis
- UI: Material-UI (MUI)

## Structure du projet

```
DEFENSEUR-IA/
├── backend/       # Backend FastAPI (Python 3.12)
│   ├── src/defenseur_ia/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── frontend/      # Application React (CRA + MUI)
│   ├── src/
│   ├── Dockerfile
│   └── .env.example
├── docs/          # Documentation technique
├── docker-compose.yml
├── init.sql
├── BACKEND_GUIDE.md
├── package.json
├── README.md
└── .gitignore
```

Notez que les dossiers et fichiers spécifiques peuvent varier en fonction des besoins de votre projet.
