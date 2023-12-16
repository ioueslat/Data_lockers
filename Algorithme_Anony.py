import pandas as pd
import hashlib
import numpy as np
import random

#code hachage
def hash_dataframe(dataframe):
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe['id'] = [hashlib.md5(f"{id_}{semaine}".encode()).hexdigest()[:8] if id_ != 'DEL' else 'DEL' for id_, semaine in zip(dataframe['id'], dataframe['Date'].dt.strftime('%Y-%U'))] 
    print(dataframe.head())
    return dataframe

#code pertubation
def pertubation(dataframe):
    dataframe['latitude'] = dataframe['latitude'].round(3) + np.random.uniform(low=0.000333, high=0.000777, size=len(dataframe))
    dataframe['longitude'] = dataframe['longitude'].round(3) + np.random.uniform(low=0.000333, high=0.000777, size=len(dataframe))
    dataframe['latitude'] += np.random.uniform(low=0.000, high=0.003, size=len(dataframe))
    dataframe['longitude'] += np.random.uniform(low=0.000, high=0.003, size=len(dataframe))
    
    return dataframe

#pertubation jours
def perturber_jours_semaine(dataframe):
    if 'Date' in dataframe.columns:
        dataframe['Date'] = pd.to_datetime(dataframe['Date'])
        jours_modifiables = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        for index, row in dataframe.iterrows():
            if row['Date'].strftime('%A') in jours_modifiables:
                if row['Date'].strftime('%A') == 'Monday':
                    dataframe.at[index, 'Date'] = row['Date'] + pd.Timedelta(days=1)
                elif row['Date'].strftime('%A') == 'Tuesday':
                    dataframe.at[index, 'Date'] = row['Date'] + pd.Timedelta(days=1)
                elif row['Date'].strftime('%A') == 'Wednesday':
                    dataframe.at[index, 'Date'] = row['Date'] + pd.Timedelta(days=1)
                elif row['Date'].strftime('%A') == 'Thursday':
                    dataframe.at[index, 'Date'] = row['Date'] - pd.Timedelta(days=3)


    dataframe.loc[dataframe['Date'].dt.day_name() == 'Saturday', 'Date'] += pd.Timedelta(days=1)
    dataframe.loc[dataframe['Date'].dt.day_name() == 'Sunday', 'Date'] -= pd.Timedelta(days=1)

    return dataframe

#perturbation heures
def perturber_heures(dataframe):
    for index, row in dataframe.iterrows():
        heure = row['Date'].hour

        
        if 9 <= heure < 11 and row['Date'].weekday() < 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(9, 11),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 14 <= heure < 16 and row['Date'].weekday() < 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(14, 16),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 12 <= heure < 14 and row['Date'].weekday() < 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(12, 14),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )

        
        elif 22 <= heure < 24:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(22, 24),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 0 <= heure < 2:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(0, 2),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 2 <= heure < 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(2, 4),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 4 <= heure < 6:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(4, 6),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        
        elif 10 <= heure < 12 and row['Date'].weekday() >= 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(10, 12),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 12 <= heure < 14 and row['Date'].weekday() >= 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(12, 14),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 14 <= heure < 16 and row['Date'].weekday() >= 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(14, 16),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )
        elif 16 <= heure < 18 and row['Date'].weekday() >= 4:
            dataframe.at[index, 'Date'] = row['Date'].replace(
                hour=np.random.randint(16, 18),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60)
            )

        # Autres plages horaires
        else:
            noise = np.random.randint(-30, 31)  # bruit aléatoire entre -30 minutes et +30 minutes
            dataframe.at[index, 'Date'] += pd.Timedelta(minutes=noise)

    return dataframe



def suppression_lignes(dataframe, pt, size):
    dataframe_copy = dataframe.copy()
    dataframe['latitude_arrondie'] = dataframe['latitude'].round(size)
    dataframe['longitude_arrondie'] = dataframe['longitude'].round(size)
    dataframe_copy['latitude'] = dataframe_copy['latitude'].round(size)
    dataframe_copy['longitude'] = dataframe_copy['longitude'].round(size)
    grouped = dataframe_copy.groupby(['latitude', 'longitude']).size().reset_index(name='count')
    grouped = grouped.sort_values(by='count', ascending=False)
    print(grouped)
    nb_cellules = int(len(grouped) * pt)
    filtered_data = grouped.head(nb_cellules)
    print(filtered_data)
    less_frequent_cells = grouped.tail(len(grouped) - nb_cellules)
    print(less_frequent_cells)

    n = 1000
    lines_to_delete = random.sample(range(len(less_frequent_cells)), min(n, len(less_frequent_cells)))

    for index, row in less_frequent_cells.iterrows():
        if index in lines_to_delete:
            lat = row['latitude']
            lon = row['longitude']
            

            row_to_delete = dataframe[(dataframe['latitude_arrondie'] == lat) & (dataframe['longitude_arrondie'] == lon) ]
            print("Ligne à supprimer :")
            print(row_to_delete)

            # Marquer la ligne pour suppression
            dataframe.loc[(dataframe['latitude_arrondie'] == lat) & (dataframe['longitude_arrondie'] == lon), 'Attribut'] = 'DEL'       
    dataframe.to_csv('dataframe_modifie.csv', index=False)  

    return dataframe
