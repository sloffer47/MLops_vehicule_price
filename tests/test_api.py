"""
Script pour tester l'API FastAPI
Exécuter avec : python tests/test_api.py
IMPORTANT : L'API doit être lancée avant : uvicorn api.app:app --reload
"""
import requests
import json
import time

# URL de base de l'API
BASE_URL = "http://127.0.0.1:8000"

def check_api_running():
    """Vérifie que l'API est accessible"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_home():
    """Teste la route d'accueil"""
    print("🏠 Test de la route d'accueil...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Réponse: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

def test_health():
    """Teste le health check"""
    print("💚 Test du health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Réponse: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

def test_prediction():
    """Teste une prédiction simple"""
    print("🔮 Test de prédiction...")
    
    car_data = {
        "year": 2020,
        "km_driven": 35000,
        "fuel": "Diesel",
        "transmission": "Automatic",
        "owner": "First",
        "engine_cc": 1500,
        "seats": 1
    }
    
    print(f"Données envoyées: {json.dumps(car_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/predict", json=car_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ RÉSULTAT:")
        print(f"   Prix prédit: {result['predicted_price']:.2f} €")
        print(f"   Confiance: {result['confidence']}")
        print(f"   Timestamp: {result['timestamp']}\n")
    else:
        print(f"❌ Erreur: {response.text}\n")

def test_batch_prediction():
    """Teste une prédiction batch"""
    print("📦 Test de prédiction batch...")
    
    cars_data = [
        {
            "year": 2020,
            "km_driven": 35000,
            "fuel": "Diesel",
            "transmission": "Automatic",
            "owner": "First",
            "engine_cc": 1500,
            "seats": 1
        },
        {
            "year": 2018,
            "km_driven": 80000,
            "fuel": "Petrol",
            "transmission": "Manual",
            "owner": "Second",
            "engine_cc": 1200,
            "seats": 10
        },
        {
            "year": 2022,
            "km_driven": 15000,
            "fuel": "Electric",
            "transmission": "Manuel",
            "owner": "First",
            "engine_cc": 10,
            "seats":1
        }
    ]
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=cars_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Nombre de voitures: {result['total_cars']}")
        
        for i, pred in enumerate(result['predictions'], 1):
            print(f"\nVoiture {i}:")
            print(f"  - Année: {pred['input_data']['year']}")
            print(f"  - Carburant: {pred['input_data']['fuel']}")
            print(f"  - Prix prédit: {pred['predicted_price']:.2f} €")
            print(f"  - Confiance: {pred['confidence']}")
    else:
        print(f"❌ Erreur: {response.text}")
    print()

def test_model_info():
    """Teste les informations du modèle"""
    print("ℹ️ Test des infos du modèle...")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        info = response.json()
        print(f"\n✅ Type de modèle: {info['model_type']}")
        print(f"   Features: {', '.join(info['features'][:5])}...")
        print(f"   Dernière mise à jour: {info['last_updated']}\n")
    else:
        print(f"❌ Erreur: {response.text}\n")

def test_example():
    """Récupère un exemple d'utilisation"""
    print("📖 Récupération d'un exemple...")
    response = requests.get(f"{BASE_URL}/example")
    
    if response.status_code == 200:
        example = response.json()
        print(f"\n✅ Exemple de requête:")
        print(json.dumps(example['example_body'], indent=2))
        print(f"\nCommande curl:\n{example['curl_command']}\n")
    else:
        print(f"❌ Erreur: {response.text}\n")

if __name__ == "__main__":
    print("="*70)
    print("🧪 TESTS DE L'API CAR PRICE PREDICTION")
    print("="*70 + "\n")
    
    # Vérifier que l'API est lancée
    print("🔍 Vérification que l'API est accessible...")
    if not check_api_running():
        print("❌ ERREUR : L'API n'est pas accessible sur http://127.0.0.1:8000\n")
        print("📝 Pour lancer l'API, ouvre un nouveau terminal et exécute :")
        print("   1. Active ton environnement : .venv\\Scripts\\activate")
        print("   2. Lance l'API : uvicorn api.app:app --reload --port 8000")
        print("   3. Relance ce script : python tests/test_api.py\n")
        print("💡 Astuce : Ouvre aussi http://127.0.0.1:8000/docs dans ton navigateur !")
        exit(1)
    
    print("✅ API accessible ! Lancement des tests...\n")
    time.sleep(0.5)
    
    try:
        test_home()
        test_health()
        test_example()
        test_prediction()
        test_batch_prediction()
        test_model_info()
        
        print("="*70)
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("="*70)
        print("\n💡 Prochaines étapes :")
        print("   - Explore l'API interactive : http://127.0.0.1:8000/docs")
        print("   - Voir MLflow : http://127.0.0.1:5000")
        print("   - Tester avec Postman ou ton appli frontend")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur : Perte de connexion avec l'API")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")