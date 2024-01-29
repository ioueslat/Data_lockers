import pandas as pd
import numpy as np
import datetime
# Lire les données à partir des fichiers CSV
# Assurez-vous que le nombre de colonnes séparées par '\t' dans 'org' est correct
df_original = pd.read_csv('org', sep='\t', header=None)
df_original.columns = ['id', 'date et heure', 'longitude', 'latitude']

# Assurez-vous que le nombre de colonnes séparées par ',' dans 'm' est correct
df_anonyme = pd.read_csv('m', sep=',', header=None)
df_anonyme.columns = ['id', 'date et heure', 'longitude', 'latitude']

# Convertir 'date et heure' en datetime
df_original['date'] = pd.to_datetime(df_original['date et heure'])
df_anonyme['date'] = pd.to_datetime(df_anonyme['date et heure'])

# Grouper par date et calculer la moyenne de la longitude et de la latitude
df_original_avg = df_original.groupby(df_original['date'].dt.date).agg({'longitude':'mean', 'latitude':'mean'})
df_anonyme_avg = df_anonyme.groupby(df_anonyme['date'].dt.date).agg({'longitude':'mean', 'latitude':'mean'})


# Initialiser un DataFrame pour stocker les scores
df_scores = pd.DataFrame(index=df_original_avg.index, columns=['score'])

# Calculer le score pour chaque jour
for date in df_scores.index:
    if date in df_anonyme_avg.index:
        # Arrondir les coordonnées à 2 chiffres après la virgule
        original_longitude = round(df_original_avg.loc[date, 'longitude'], 4)
        original_latitude = round(df_original_avg.loc[date, 'latitude'], 4)
        anonyme_longitude = round(df_anonyme_avg.loc[date, 'longitude'], 4)
        anonyme_latitude = round(df_anonyme_avg.loc[date, 'latitude'], 4)
        
        if (anonyme_longitude <= original_longitude) and (anonyme_latitude <= original_latitude):
            df_scores.loc[date, 'score'] = 1
        else:
            df_scores.loc[date, 'score'] = 0
    else:
        df_scores.loc[date, 'score'] = np.nan

# Calculer le score total
score_total = df_scores['score'].sum()

# Obtenir le nombre total de jours
nombre_total_de_jours = len(df_scores)

# Calculer le score moyen
score_moyen = score_total / nombre_total_de_jours

# Afficher le score moyen avec une précision de 10 chiffres après la virgule
print(f"Le score moyen d'utilité est {score_moyen:.30f}")
