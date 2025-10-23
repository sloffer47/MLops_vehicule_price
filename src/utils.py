import joblib
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
