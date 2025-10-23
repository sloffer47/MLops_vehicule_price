import pandas as pd
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
