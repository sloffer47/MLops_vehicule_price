import pandas as pd
from tabulate import tabulate

# Chargement du fichier CSV
df = pd.read_csv("data/raw/car_data.csv").head(10)


# Affichage sous forme de table
print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
