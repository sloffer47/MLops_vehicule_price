"""
Script d'entraînement avec tracking MLflow
Permet de comparer différents modèles et hyperparamètres
"""
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import sys
import os

# Ajouter le dossier src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.preprocess import prepare_data

def evaluate_model(model, X_test, y_test):
    """Évalue un modèle et retourne les métriques"""
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, predictions)
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2
    }

def train_model(model_type='random_forest', **kwargs):
    """
    Entraîne un modèle avec MLflow tracking
    
    Args:
        model_type: 'random_forest', 'gradient_boosting', ou 'ridge'
        **kwargs: Hyperparamètres du modèle
    """
    # 1️⃣ Préparer les données
    print("📊 Préparation des données...")
    X_train, X_test, y_train, y_test, preprocessor = prepare_data()
    
    # 2️⃣ Configurer MLflow
    mlflow.set_experiment("car_price_prediction")
    
    with mlflow.start_run(run_name=f"{model_type}_experiment"):
        
        # 3️⃣ Créer le modèle selon le type
        if model_type == 'random_forest':
            model = RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', None),
                random_state=42
            )
        elif model_type == 'gradient_boosting':
            model = GradientBoostingRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                learning_rate=kwargs.get('learning_rate', 0.1),
                max_depth=kwargs.get('max_depth', 3),
                random_state=42
            )
        elif model_type == 'ridge':
            model = Ridge(
                alpha=kwargs.get('alpha', 1.0),
                random_state=42
            )
        else:
            raise ValueError(f"Type de modèle inconnu : {model_type}")
        
        # 4️⃣ Logger les paramètres
        mlflow.log_param("model_type", model_type)
        for key, value in kwargs.items():
            mlflow.log_param(key, value)
        
        # 5️⃣ Entraîner le modèle
        print(f"🏋️ Entraînement du modèle {model_type}...")
        model.fit(X_train, y_train)
        
        # 6️⃣ Évaluer le modèle
        metrics = evaluate_model(model, X_test, y_test)
        print(f"\n📈 Résultats :")
        print(f"  MAE:  {metrics['mae']:.2f} €")
        print(f"  RMSE: {metrics['rmse']:.2f} €")
        print(f"  R²:   {metrics['r2']:.4f}")
        
        # 7️⃣ Logger les métriques
        mlflow.log_metric("mae", metrics['mae'])
        mlflow.log_metric("rmse", metrics['rmse'])
        mlflow.log_metric("r2", metrics['r2'])
        
        # 8️⃣ Sauvegarder le modèle dans MLflow
        mlflow.sklearn.log_model(model, "model")
        
        # 9️⃣ Sauvegarder aussi localement si c'est le meilleur
        import joblib
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/production_model.pkl')
        preprocessor.save('models/preprocessor.pkl')
        
        print(f"\n✅ Modèle sauvegardé !")
        print(f"📂 MLflow UI : mlflow ui --port 5000")
        
        return model, metrics

def compare_models():
    """Compare plusieurs modèles et affiche les résultats"""
    print("🔬 Comparaison de plusieurs modèles...\n")
    
    experiments = [
        {'model_type': 'random_forest', 'n_estimators': 50, 'max_depth': 10},
        {'model_type': 'random_forest', 'n_estimators': 100, 'max_depth': 15},
        {'model_type': 'gradient_boosting', 'n_estimators': 100, 'learning_rate': 0.1},
        {'model_type': 'ridge', 'alpha': 1.0}
    ]
    
    results = []
    for exp in experiments:
        print(f"\n{'='*60}")
        print(f"Test : {exp}")
        print('='*60)
        model, metrics = train_model(**exp)
        results.append({**exp, **metrics})
    
    # Afficher le résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES EXPÉRIENCES")
    print("="*80)
    results_sorted = sorted(results, key=lambda x: x['rmse'])
    for i, r in enumerate(results_sorted, 1):
        print(f"\n{i}. {r['model_type']} - RMSE: {r['rmse']:.2f} € - R²: {r['r2']:.4f}")
        print(f"   Paramètres: {', '.join([f'{k}={v}' for k,v in r.items() if k not in ['mae','rmse','r2','model_type']])}")
    
    print("\n🏆 Meilleur modèle sauvegardé dans models/production_model.pkl")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'compare':
        # Mode comparaison : python src/train.py compare
        compare_models()
    else:
        # Mode simple : python src/train.py
        train_model(model_type='random_forest', n_estimators=100, max_depth=15)