# Python 3.12 slim pour taille réduite et rapidité de build
FROM python:3.12-slim

# Variables d'environnement standard
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cache des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des dossiers utiles
RUN mkdir -p logs data

# Utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000

# Démarrage dynamique prenant en compte la variable PORT de Render (par défaut 8000)
CMD ["sh", "-c", "uvicorn agentic:app --host 0.0.0.0 --port ${PORT:-8000}"]
