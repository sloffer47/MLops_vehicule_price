import os
from src.preprocess import prepare_data
from src.train import train_model

def test_prepare_data():
    X_train, X_test, y_train, y_test, preprocessor = prepare_data()
    assert not X_train.empty

def test_train_model():
    train_model()
    assert os.path.exists('models/production_model.pkl')
