# Dockerfile pour MLops Vehicule Price API

# 1️⃣ Image de base légère avec Python
FROM python:3.11-slim

# 2️⃣ Variables d'environnement pour éviter les prompts pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

# 3️⃣ Créer le dossier de l'application
WORKDIR /app

# 4️⃣ Copier les fichiers requirements
COPY requirements.txt .

# 5️⃣ Installer les dépendances
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copier le code source
COPY . .

# 7️⃣ Créer les dossiers pour modèles et données ...
RUN mkdir -p models data/processed data/raw

# 8️⃣ Exposer le port FastAPI
EXPOSE 8000

# 9️⃣ Lancer l'application avec uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
