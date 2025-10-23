import pandas as pd
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
