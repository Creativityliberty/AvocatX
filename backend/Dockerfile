FROM python:3.12-slim

# Répertoire de travail
WORKDIR /app

# Eviter la génération de .pyc et buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier Poetry config
COPY pyproject.toml poetry.lock ./

# Installer Poetry et deps
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copier le code source
COPY src/ ./src/

# Répertoire d'uploads
RUN mkdir -p /app/uploads

# Exposer le port API
EXPOSE 8000

# Démarrage du backend FastAPI
CMD ["python", "-m", "uvicorn", "src.defenseur_ia.main:app", "--host", "0.0.0.0", "--port", "8000"]
