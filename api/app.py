"""
API FastAPI pour servir le modèle de prédiction de prix de voitures
Lancer avec : uvicorn api.app:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import pandas as pd
import sys
import os
from datetime import datetime

# Ajouter le dossier parent au path pour importer src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.preprocess import DataPreprocessor

# 🚀 Initialisation de l'API
app = FastAPI(
    title="🚗 Car Price Prediction API",
    description="API MLOps pour prédire le prix des voitures d'occasion",
    version="1.0.0"
)

# 📦 Chargement du modèle et du preprocessor
try:
    model = joblib.load('models/production_model.pkl')
    preprocessor = DataPreprocessor.load('models/preprocessor.pkl')
    print("✅ Modèle et preprocessor chargés avec succès")
except Exception as e:
    print(f"❌ Erreur de chargement : {e}")
    model = None
    preprocessor = None

# 📊 Schéma de données pour la validation
class CarInput(BaseModel):
    year: int = Field(..., ge=2000, le=2024, description="Année de fabrication")
    km_driven: int = Field(..., ge=0, le=500000, description="Kilomètres parcourus")
    fuel: str = Field(..., description="Type de carburant (Petrol, Diesel, Electric, Hybrid)")
    transmission: str = Field(..., description="Type de transmission (Manual, Automatic)")
    owner: str = Field(..., description="Type de propriétaire (First, Second, Third)")
    engine_cc: int = Field(..., description="Cylindrée du moteur")
    seats: int = Field(..., ge=2, le=8, description="Nombre de sièges")
    
    class Config:
        schema_extra = {
            "example": {
                "year": 2020,
                "km_driven": 35000,
                "fuel": "Diesel",
                "transmission": "Automatic",
                "owner": "First",
                "engine_cc": 1500,
                "seats": 5
            }
        }

class PredictionResponse(BaseModel):
    predicted_price: float
    confidence: str
    input_data: dict
    timestamp: str

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_cars: int

# 🏠 Route principale
@app.get("/")
def home():
    """Page d'accueil de l'API"""
    return {
        "message": "🚗 Bienvenue sur l'API Car Price Prediction",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "batch_predict": "/predict/batch (POST)",
            "model_info": "/model/info",
            "docs": "/docs"
        }
    }

# 💚 Health check
@app.get("/health")
def health_check():
    """Vérifie que l'API et le modèle sont opérationnels"""
    if model is None or preprocessor is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": datetime.now().isoformat()
    }

# 🔮 Prédiction simple
@app.post("/predict", response_model=PredictionResponse)
def predict_price(car: CarInput):
    """
    Prédit le prix d'une voiture
    
    Args:
        car: Données de la voiture (CarInput)
    
    Returns:
        PredictionResponse avec le prix prédit
    """
    if model is None or preprocessor is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        # Convertir en DataFrame
        input_df = pd.DataFrame([car.dict()])
        
        # Prétraiter
        X = preprocessor.transform(input_df)
        
        # Prédire
        prediction = model.predict(X)[0]
        
        # Déterminer le niveau de confiance (simplifié)
        if 10000 <= prediction <= 50000:
            confidence = "high"
        elif 5000 <= prediction <= 70000:
            confidence = "medium"
        else:
            confidence = "low"
        
        return PredictionResponse(
            predicted_price=round(prediction, 2),
            confidence=confidence,
            input_data=car.dict(),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {str(e)}")

# 📦 Prédiction batch
@app.post("/predict/batch", response_model=BatchPredictionResponse)
def batch_predict(cars: List[CarInput]):
    """
    Prédit le prix de plusieurs voitures en une seule requête
    
    Args:
        cars: Liste de voitures (List[CarInput])
    
    Returns:
        BatchPredictionResponse avec toutes les prédictions
    """
    if model is None or preprocessor is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        predictions = []
        for car in cars:
            result = predict_price(car)
            predictions.append(result)
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_cars=len(predictions)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur batch : {str(e)}")

# ℹ️ Informations sur le modèle
@app.get("/model/info")
def model_info():
    """Retourne les informations sur le modèle en production"""
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    return {
        "model_type": type(model).__name__,
        "features": preprocessor.feature_names if preprocessor else [],
        "model_params": model.get_params() if hasattr(model, 'get_params') else {},
        "last_updated": "2025-01-15"  # À adapter avec une vraie date
    }

# 🧹 Recharger le modèle (utile pour le déploiement continu)
@app.post("/model/reload")
def reload_model():
    """Recharge le modèle depuis le disque"""
    global model, preprocessor
    try:
        model = joblib.load('models/production_model.pkl')
        preprocessor = DataPreprocessor.load('models/preprocessor.pkl')
        return {
            "status": "success",
            "message": "Modèle rechargé avec succès",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de rechargement : {str(e)}")

# 🎯 Exemple d'utilisation
@app.get("/example")
def get_example():
    """Retourne un exemple de requête pour /predict"""
    return {
        "endpoint": "/predict",
        "method": "POST",
        "example_body": {
            "year": 2020,
            "km_driven": 35000,
            "fuel": "Diesel",
            "transmission": "Automatic",
            "owner": "First",
            "engine_cc": 1500,
            "seats": 5
        },
        "curl_command": """
curl -X POST "http://localhost:8000/predict" \\
  -H "Content-Type: application/json" \\
  -d '{
    "year": 2020,
    "km_driven": 35000,
    "fuel": "Diesel",
    "transmission": "Automatic",
    "owner": "First",
    "engine_cc": 1500,
    "seats": 5
  }'
        """
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)