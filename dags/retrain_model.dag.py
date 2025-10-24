from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import pickle
import os
from pathlib import Path

def fetch_new_data():
    """Récupère nouvelles données"""
    # TODO: Adapter selon ta source de données
    # Exemple : scraping, API, téléchargement CSV
    
    print("📥 Récupération des nouvelles données...")
    # Simule nouvelles données (à adapter)
    df = pd.read_csv("/opt/airflow/data/raw/vehicules.csv")  # Adapte le chemin
    
    # Sauvegarde
    df.to_csv("/opt/airflow/data/new_data.csv", index=False)
    print(f"✅ {len(df)} données récupérées")

def preprocess_data():
    """Nettoie les données"""
    print("🧹 Preprocessing des données...")
    
    df = pd.read_csv("/opt/airflow/data/new_data.csv")
    
    # Ton preprocessing (adapte selon ton code)
    df = df.dropna()
    df = df[df['price'] > 0]
    
    df.to_csv("/opt/airflow/data/processed.csv", index=False)
    print(f"✅ {len(df)} données nettoyées")

def train_model():
    """Entraîne le nouveau modèle"""
    print("🔨 Entraînement du modèle...")
    
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    
    # Charge données
    df = pd.read_csv("/opt/airflow/data/processed.csv")
    
    # TODO: Adapter selon tes features
    X = df.drop(['price'], axis=1)  # Adapte les colonnes
    y = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraîne
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Évalue
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"📊 Nouveau modèle - MAE: {mae:.2f}, R²: {r2:.3f}")
    
    # Sauvegarde temporaire
    with open("/opt/airflow/models/model_new.pkl", "wb") as f:
        pickle.dump(model, f)
    
    # Sauvegarde métriques pour comparaison
    with open("/opt/airflow/models/metrics_new.txt", "w") as f:
        f.write(f"{mae},{r2}")

def evaluate_and_deploy():
    """Compare et déploie si meilleur"""
    print("📊 Évaluation et comparaison...")
    
    # Charge ancien modèle
    old_model_path = "/opt/airflow/models/model.pkl"
    new_model_path = "/opt/airflow/models/model_new.pkl"
    
    if not os.path.exists(old_model_path):
        # Premier entraînement
        print("🎉 Premier modèle → Déploiement automatique")
        os.rename(new_model_path, old_model_path)
        os.system("docker restart vehicule_price_api")
        return
    
    # Compare les métriques
    with open("/opt/airflow/models/metrics_new.txt", "r") as f:
        mae_new, r2_new = map(float, f.read().strip().split(','))
    
    # Charge données test
    df = pd.read_csv("/opt/airflow/data/processed.csv")
    X = df.drop(['price'], axis=1)
    y = df['price']
    
    # Évalue ancien modèle
    with open(old_model_path, "rb") as f:
        model_old = pickle.load(f)
    
    from sklearn.metrics import mean_absolute_error
    mae_old = mean_absolute_error(y, model_old.predict(X))
    
    print(f"📊 Ancien modèle - MAE: {mae_old:.2f}")
    print(f"📊 Nouveau modèle - MAE: {mae_new:.2f}")
    
    # Décision
    if mae_new < mae_old:
        improvement = ((mae_old - mae_new) / mae_old) * 100
        print(f"✅ Nouveau modèle MEILLEUR ({improvement:.1f}% amélioration)")
        
        # Remplace le modèle
        os.rename(new_model_path, old_model_path)
        
        # Redémarre l'API
        os.system("docker restart vehicule_price_api")
        print("🚀 API redémarrée avec le nouveau modèle")
    else:
        print(f"⚠️ Ancien modèle reste meilleur, pas de déploiement")
        os.remove(new_model_path)

def cleanup():
    """Nettoie les fichiers temporaires"""
    print("🧹 Nettoyage...")
    files_to_clean = [
        "/opt/airflow/data/new_data.csv",
        "/opt/airflow/data/processed.csv",
        "/opt/airflow/models/metrics_new.txt"
    ]
    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)
    print("✅ Nettoyage terminé")

# DAG
dag = DAG(
    'retrain_vehicule_model',
    description='Re-entraîne le modèle automatiquement',
    schedule_interval='0 6 * * 1',  # Chaque lundi 6h
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args={
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    tags=['ml', 'retrain']
)

# Tasks
t1 = PythonOperator(task_id='fetch_data', python_callable=fetch_new_data, dag=dag)
t2 = PythonOperator(task_id='preprocess', python_callable=preprocess_data, dag=dag)
t3 = PythonOperator(task_id='train', python_callable=train_model, dag=dag)
t4 = PythonOperator(task_id='evaluate_deploy', python_callable=evaluate_and_deploy, dag=dag)
t5 = PythonOperator(task_id='cleanup', python_callable=cleanup, dag=dag)

# Pipeline
t1 >> t2 >> t3 >> t4 >> t5