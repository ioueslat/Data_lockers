import pandas as pd
import numpy as np
from scipy.stats import wasserstein_distance

# Fonction pour générer les positions moyennes pour les samedis de chaque semaine
def generate_weekly_average_positions(data):
    data['date'] = pd.to_datetime(data['date'])
    data = data[data['date'].dt.dayofweek == 5]  
    if data.empty:
        return []

    data['week'] = data['date'].dt.isocalendar().week
    weekly_positions = []
    for week in data['week'].unique():
        week_data = data[data['week'] == week]
        week_positions = {}
        for identifier in week_data['identifier'].unique():
            identifier_data = week_data[week_data['identifier'] == identifier]
            average_longitude = identifier_data['longitude'].mean()
            average_latitude = identifier_data['latitude'].mean()
            week_positions[identifier] = (average_longitude, average_latitude)
        weekly_positions.append({week: week_positions})
    return weekly_positions

# Fonction pour calculer la distance de Wasserstein entre les semaines
def calculate_wasserstein_distance_for_weeks(original_list, anon_list):
    if not original_list or not anon_list:
        return np.nan  # Retourne NaN si une des listes est vide

    wasserstein_distances = []
    for original_week_dict, anon_week_dict in zip(original_list, anon_list):
        for week in original_week_dict:
            if week in anon_week_dict:
                orig_positions = np.array(list(original_week_dict[week].values()))
                anon_positions = np.array(list(anon_week_dict[week].values()))
                if orig_positions.size > 0 and anon_positions.size > 0:
                    distance_longitude = wasserstein_distance(orig_positions[:, 0], anon_positions[:, 0])
                    distance_latitude = wasserstein_distance(orig_positions[:, 1], anon_positions[:, 1])
                    avg_distance = (distance_longitude + distance_latitude) / 2
                    wasserstein_distances.append(avg_distance)

    return np.mean(wasserstein_distances) if wasserstein_distances else np.nan


# Chargement des données originales
col_names = ['identifier', 'date', 'longitude', 'latitude']
df_original = pd.read_csv('org', names=col_names, header=None, sep='\t')
print(f"Nombre d'enregistrements originaux avant le filtrage: {len(df_original)}")
original_weekly_positions = generate_weekly_average_positions(df_original)
print(f"Nombre de semaines dans les données originales après le filtrage: {len(original_weekly_positions)}")

# Chargement et nettoyage des données anonymisées
df_anon = pd.read_csv('aaa', names=col_names, header=None, sep='\t')
df_anon = df_anon[df_anon['identifier'] != 'DEL']
print(f"Nombre d'enregistrements anonymisés avant le filtrage: {len(df_anon)}")
anon_weekly_positions = generate_weekly_average_positions(df_anon)
print(f"Nombre de semaines dans les données anonymisées après le filtrage: {len(anon_weekly_positions)}")


# Calcul du score et affichage
wasserstein_score = calculate_wasserstein_distance_for_weeks(original_weekly_positions, anon_weekly_positions)
if np.isnan(wasserstein_score):
    print("Impossible de calculer le score de similarité en raison de données insuffisantes ou non valides.")
else:
    similarity_score = 1 / (1 + wasserstein_score)
    print(f"Score de similarité (Wasserstein) : {similarity_score}")

# Affichage des positions hebdomadaires
print("Positions hebdomadaires originales :")
print(original_weekly_positions)
print("\nPositions hebdomadaires anonymisées :")
print(anon_weekly_positions)
