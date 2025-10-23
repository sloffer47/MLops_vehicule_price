# Projet MLOps - Prédiction Prix Voitures

Projet complet pour prédire le prix des voitures d'occasion avec MLOps.

## Structure du projet
├── data/
├── models/
├── notebooks/
├── src/
├── tests/
├── api/
├── monitoring/
├── configs/
├── requirements.txt
└── README.md

## Installation
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt

## Génération des données
python src/download_data.py

## Entraînement
python src/train.py

## Lancer l'API
uvicorn api.app:app --reload

## Tests
pytest tests/
