# Guide de Démarrage Rapide - Backend DEFENSEUR-IA

## Installation et Configuration

### 1. Installation des dépendances

```bash
# Installation de Poetry (si pas déjà installé)
curl -sSL https://install.python-poetry.org | python3 -

# Installation des dépendances
poetry install

# Activation de l'environnement virtuel
poetry shell
```

### 2. Configuration des variables d'environnement

Créer un fichier `.env` à la racine:

```bash
# Base de données
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=defenseur_ia
POSTGRES_USER=defenseur
POSTGRES_PASSWORD=defenseur123

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Légifrance
LEGIFRANCE_API_KEY=your-legifrance-key
LEGIFRANCE_API_SECRET=your-legifrance-secret
```

### 3. Démarrage avec Docker (Recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

### 4. Démarrage Manuel

#### 4.1 Démarrer PostgreSQL
```bash
# Sur macOS avec Homebrew
brew services start postgresql

# Créer la base de données
createdb defenseur_ia
```

#### 4.2 Démarrer Redis
```bash
# Sur macOS avec Homebrew
brew services start redis
```

#### 4.3 Lancer le backend
```bash
# Option 1: Avec Poetry
poetry run python -m uvicorn src.defenseur_ia.main:app --reload

# Option 2: Avec Python directement
python -m uvicorn src.defenseur_ia.main:app --reload

# Option 3: Avec le script de démarrage
python start_backend.py
```

### 5. Vérification de l'installation

```bash
# Tester l'API
curl http://localhost:8000/health

# Tester la liste des dossiers
curl http://localhost:8000/api/v1/cases

# Documentation Swagger
# Ouvrir: http://localhost:8000/docs
```

## Structure des endpoints API

### Dossiers (Cases)
- `GET /api/v1/cases` - Liste des dossiers
- `POST /api/v1/cases` - Créer un dossier
- `GET /api/v1/cases/{id}` - Dossier spécifique
- `PUT /api/v1/cases/{id}` - Mettre à jour
- `DELETE /api/v1/cases/{id}` - Supprimer

### Documents
- `POST /api/v1/cases/{id}/documents` - Upload document
- `GET /api/v1/cases/{id}/documents` - Liste documents
- `GET /api/v1/documents/{id}` - Document spécifique

### Pipeline
- `GET /api/v1/cases/{id}/status` - Statut pipeline
- `POST /api/v1/cases/{id}/pipeline/start` - Démarrer
- `POST /api/v1/cases/{id}/pipeline/stop` - Arrêter

### WebSocket
- `WS /ws/{dossier_id}` - Monitoring temps réel

## Exemples d'utilisation

### 1. Créer un dossier
```bash
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Recours OQTF",
    "description": "Recours contre une OQTF",
    "client_email": "client@example.com",
    "type_contentieux": "OQTF"
  }'
```

### 2. Upload un document
```bash
curl -X POST http://localhost:8000/api/v1/cases/{dossier_id}/documents \
  -F "file=@document.pdf" \
  -F "type_document=preuve" \
  -F "description=Document justificatif"
```

### 3. Démarrer le pipeline
```bash
curl -X POST http://localhost:8000/api/v1/cases/{dossier_id}/pipeline/start
```

## Configuration du frontend

### 1. Mettre à jour l'URL de l'API
Dans le frontend React, mettre à jour le fichier `.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

### 2. Installer et lancer le frontend
```bash
cd ../avocatx
npm install
npm start
```

## Dépannage

### Problèmes courants

#### 1. Erreur de connexion PostgreSQL
```bash
# Vérifier que PostgreSQL est en cours d'exécution
ps aux | grep postgres

# Créer la base de données manuellement
createdb defenseur_ia
```

#### 2. Erreur de connexion Redis
```bash
# Vérifier que Redis est en cours d'exécution
redis-cli ping

# Redémarrer Redis
brew services restart redis
```

#### 3. Erreur d'import Python
```bash
# Vérifier la structure du projet
python -c "import sys; sys.path.append('src'); from defenseur_ia.main import app; print('✅ Import réussi')"
```

### Logs et debugging

```bash
# Voir les logs détaillés
export LOG_LEVEL=DEBUG
python -m uvicorn src.defenseur_ia.main:app --reload --log-level debug

# Voir les logs Docker
docker-compose logs -f backend
```

## Scripts utilitaires

### Script de démarrage rapide
```bash
#!/bin/bash
# start_backend.sh

echo "🚀 Démarrage du backend DEFENSEUR-IA..."

# Vérifier les services
echo "📊 Vérification des services..."

# PostgreSQL
if pg_isready -h localhost -p 5432; then
    echo "✅ PostgreSQL est en cours d'exécution"
else
    echo "❌ PostgreSQL n'est pas accessible"
    exit 1
fi

# Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis est en cours d'exécution"
else
    echo "❌ Redis n'est pas accessible"
    exit 1
fi

# Lancer le backend
echo "🚀 Lancement du backend FastAPI..."
python -m uvicorn src.defenseur_ia.main:app --reload --host 0.0.0.0 --port 8000
```

### Script de test
```bash
#!/bin/bash
# test_api.sh

echo "🧪 Test de l'API..."

# Test health check
response=$(curl -s http://localhost:8000/health)
echo "Health check: $response"

# Test création dossier
response=$(curl -s -X POST http://localhost:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Test API"}')
echo "Création dossier: $response"

echo "✅ Tests terminés"
```

## Support et aide

- Documentation Swagger: http://localhost:8000/docs
- Documentation ReDoc: http://localhost:8000/redoc
- Logs: `docker-compose logs -f backend`
- Issues: Créer une issue sur le repository GitHub
