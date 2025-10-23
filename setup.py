"""
Script setup.py pour créer un projet MLOps complet
Exécuter avec : python setup.py
"""

import os

def create_directory(path):
    os.makedirs(path, exist_ok=True)
    print(f"✓ Dossier créé : {path}")

def create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Fichier créé : {path}")

def setup_project():
    print("🚀 Création du projet MLOps complet...")

    # 1️⃣ Créer les dossiers
    folders = [
        "data/raw", "data/processed",
        "models", "notebooks", "src",
        "tests", "api", "monitoring",
        "configs", "mlruns"
    ]
    for folder in folders:
        create_directory(folder)
    create_file("src/__init__.py", "")
    create_file("api/__init__.py", "")
    create_file("monitoring/__init__.py", "")

    # 2️⃣ README.md
    readme_content = """# Projet MLOps - Prédiction Prix Voitures

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
venv\\Scripts\\activate    # Windows
pip install -r requirements.txt

## Génération des données
python src/download_data.py

## Entraînement
python src/train.py

## Lancer l'API
uvicorn api.app:app --reload

## Tests
pytest tests/
"""
    create_file("README.md", readme_content)

    # 3️⃣ requirements.txt
    requirements_content = """pandas
numpy
scikit-learn
mlflow
fastapi
uvicorn
pydantic
python-multipart
joblib
evidently
matplotlib
seaborn
pytest
httpx
pyyaml
requests
"""
    create_file("requirements.txt", requirements_content)

    # 4️⃣ src/download_data.py
    download_data_content = """import pandas as pd
import numpy as np
import os

def download_car_data():
    np.random.seed(42)
    n_samples = 1000
    data = {
        'year': np.random.randint(2010, 2024, n_samples),
        'km_driven': np.random.randint(5000, 200000, n_samples),
        'fuel': np.random.choice(['Petrol','Diesel','Electric','Hybrid'], n_samples),
        'transmission': np.random.choice(['Manual','Automatic'], n_samples),
        'owner': np.random.choice(['First','Second','Third'], n_samples),
        'engine_cc': np.random.choice([1000,1200,1500,2000,2500], n_samples),
        'seats': np.random.choice([4,5,7], n_samples)
    }
    df = pd.DataFrame(data)
    base_price = 15000
    df['price'] = (base_price + (df['year']-2010)*1000
                   - df['km_driven']*0.05
                   + (df['fuel']=='Electric').astype(int)*5000
                   + (df['transmission']=='Automatic').astype(int)*2000
                   + (df['owner']=='First').astype(int)*3000
                   + df['engine_cc']*2
                   + df['seats']*500
                   + np.random.normal(0,2000,n_samples))
    df['price'] = df['price'].clip(lower=5000).round(0).astype(int)
    os.makedirs('data/raw', exist_ok=True)
    df.to_csv('data/raw/car_data.csv', index=False)
    print("✅ Données sauvegardées : data/raw/car_data.csv")
    return df

if __name__ == '__main__':
    download_car_data()
"""
    create_file("src/download_data.py", download_data_content)

    # 5️⃣ src/preprocess.py
    preprocess_content = """import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

class DataPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = None

    def fit_transform(self, df):
        df = df.copy()
        X = df.drop('price', axis=1)
        y = df['price']
        categorical_cols = X.select_dtypes(include=['object']).columns
        numerical_cols = X.select_dtypes(include=['int64','float64']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le
        X[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])
        self.feature_names = X.columns.tolist()
        return X, y

    def transform(self, df):
        df = df.copy()
        categorical_cols = df.select_dtypes(include=['object']).columns
        numerical_cols = df.select_dtypes(include=['int64','float64']).columns
        for col in categorical_cols:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                df[col] = df[col].astype(str).apply(lambda x: x if x in le.classes_ else le.classes_[0])
                df[col] = le.transform(df[col])
        df[numerical_cols] = self.scaler.transform(df[numerical_cols])
        return df

    def save(self, path='models/preprocessor.pkl'):
        joblib.dump(self, path)

    @staticmethod
    def load(path='models/preprocessor.pkl'):
        return joblib.load(path)

def prepare_data(data_path='data/raw/car_data.csv', test_size=0.2):
    df = pd.read_csv(data_path)
    preprocessor = DataPreprocessor()
    X, y = preprocessor.fit_transform(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    os.makedirs('data/processed', exist_ok=True)
    train_df = X_train.copy(); train_df['price']=y_train; train_df.to_csv('data/processed/train.csv', index=False)
    test_df = X_test.copy(); test_df['price']=y_test; test_df.to_csv('data/processed/test.csv', index=False)
    preprocessor.save()
    return X_train, X_test, y_train, y_test, preprocessor

if __name__=='__main__':
    prepare_data()
"""
    create_file("src/preprocess.py", preprocess_content)

    # 6️⃣ src/utils.py
    utils_content = """import joblib
import pandas as pd

def load_model(path='models/production_model.pkl'):
    return joblib.load(path)

def load_preprocessor(path='models/preprocessor.pkl'):
    return joblib.load(path)

def predict(model, preprocessor, input_data):
    if isinstance(input_data, dict):
        input_data = pd.DataFrame([input_data])
    X = preprocessor.transform(input_data)
    return model.predict(X)[0]
"""
    create_file("src/utils.py", utils_content)

    # 7️⃣ src/train.py
    train_content = """from preprocess import prepare_data
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_model():
    X_train, X_test, y_train, y_test, preprocessor = prepare_data()
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/production_model.pkl')
    print("✅ Modèle sauvegardé : models/production_model.pkl")
    preprocessor.save('models/preprocessor.pkl')

if __name__=='__main__':
    train_model()
"""
    create_file("src/train.py", train_content)

    # 8️⃣ tests/test_pipeline.py
    test_content = """import os
from src.preprocess import prepare_data
from src.train import train_model

def test_prepare_data():
    X_train, X_test, y_train, y_test, preprocessor = prepare_data()
    assert not X_train.empty

def test_train_model():
    train_model()
    assert os.path.exists('models/production_model.pkl')
"""
    create_file("tests/test_pipeline.py", test_content)

    print("\n✅ Projet MLOps créé avec tous les fichiers Python remplis!")

if __name__ == "__main__":
    setup_project()
