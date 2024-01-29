import pandas as pd
import numpy as np
import datetime

# Lire les données à partir des fichiers CSV
df_original = pd.read_csv('insanonym', sep='\t')
# Renommer les colonnes du DataFrame original
df_original.columns = ['id', 'date et heure', 'longitude', 'latitude']

df_anonyme = pd.read_csv('soum2', sep=',')

# Renommer les colonnes du DataFrame anonyme
df_anonyme.columns = ['id', 'date et heure', 'longitude', 'latitude']

import pandas as pd
import numpy as np
from scipy.spatial import distance
from random import uniform

# Fonction pour calculer la vitesse
def calculate_speed(df):
    df = df.sort_values('date et heure')
    df[['lat_shifted', 'lon_shifted', 'time_shifted']] = df[['latitude', 'longitude', 'date et heure']].shift(-1)
    df['distance'] = np.sqrt((df['latitude'] - df['lat_shifted'])**2 + (df['longitude'] - df['lon_shifted'])**2)
    df['date et heure'] = pd.to_datetime(df['date et heure'])
    df['time_shifted'] = pd.to_datetime(df['time_shifted'])
    df['time_diff'] = (df['time_shifted'] - df['date et heure']).dt.total_seconds() / 3600
    df.loc[df['time_diff'] != 0, 'speed'] = df['distance'] / df['time_diff']
    df = df.dropna(subset=['speed'])
    return df

# Fonction pour calculer le score hebdomadaire
def calculate_weekly_score(df_original, df_anonyme):
    df_original_avg = df_original.resample('W', on='date et heure')['speed'].mean()
    df_anonyme_avg = df_anonyme.resample('W', on='date et heure')['speed'].mean()
    speed_difference = (df_original_avg - df_anonyme_avg).abs()
    df_scores = 1 / (1 + speed_difference)
    df_scores.fillna(0, inplace=True)
    return df_scores

# Calculer la vitesse pour chaque DataFrame
df_original_grouped = df_original.groupby(pd.Grouper(key='date et heure', freq='W'))
df_anonyme_grouped = df_anonyme.groupby(pd.Grouper(key='date et heure', freq='W'))

df_original = pd.concat([calculate_speed(group) for _, group in df_original_grouped])
df_anonyme = pd.concat([calculate_speed(group) for _, group in df_anonyme_grouped])

# Calculer le score hebdomadaire
df_scores = calculate_weekly_score(df_original, df_anonyme)

# Calculer le score total
score_total = df_scores.sum()

# Obtenir le nombre total de jours
nombre_total_de_jours = len(df_scores)

# Calculer le score moyen
score_moyen = score_total / nombre_total_de_jours

# Afficher le score moyen avec une précision de 10 chiffres après la virgule
print(f"Le score moyen d'utilité est {score_moyen:.10f}")