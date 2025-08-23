FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    make \\
    libpq-dev \\
    libmagic1 \\
    poppler-utils \\
    tesseract-ocr \\
    tesseract-ocr-fra \\
    ffmpeg \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de configuration
COPY pyproject.toml poetry.lock ./

# Installer Poetry
RUN pip install poetry

# Configurer Poetry
RUN poetry config virtualenvs.create false

# Installer les dépendances
RUN poetry install --no-dev

# Copier le code source
COPY src/ ./src/
COPY init.sql ./

# Créer le répertoire uploads
RUN mkdir -p /app/uploads

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["python", "-m", "uvicorn", "src.defenseur_ia.main:app", "--host", "0.0.0.0", "--port", "8000"]
