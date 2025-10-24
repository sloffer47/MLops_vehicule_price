# Dockerfile pour MLops Vehicule Price API

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p models data/processed data/raw

EXPOSE 8000

# ✅ Correction ici : plus de "src."
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
