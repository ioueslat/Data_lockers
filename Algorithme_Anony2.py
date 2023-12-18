import pandas as pd
import numpy as np
import hashlib
import random

def creer_dataframe_de_fichier(nom_fichier):
    try:
        dataframe = pd.read_csv(nom_fichier, delimiter='\t', header=None, names=['id', 'Date', 'longitude', 'latitude'],dtype={'longitude': 'object', 'latitude': 'object'})
        dataframe['Date'] = pd.to_datetime(dataframe['Date'])
        dataframe = dataframe.astype({'longitude': 'float64', 'latitude': 'float64'})
        dataframe['semaine'] = dataframe['Date'].dt.strftime('%Y-%U')
        return dataframe
    except FileNotFoundError:
        print("Le fichier spécifié est introuvable.")
        return None
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return None

def hash_dataframe(dataframe):
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe['id'] = [hashlib.md5(f"{id_}{semaine}".encode()).hexdigest()[:8] if id_ != 'DEL' else 'DEL' for id_, semaine in zip(dataframe['id'], dataframe['Date'].dt.strftime('%Y-%U'))]
    return dataframe



#code pertubation
def pertubation(dataframe):
    dataframe['latitude'] = dataframe['latitude'].round(3) + np.random.uniform(low=0.000333, high=0.000777, size=len(dataframe))
    dataframe['longitude'] = dataframe['longitude'].round(3) + np.random.uniform(low=0.000333, high=0.000777, size=len(dataframe))
    
    return dataframe

#pertubation jours:

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
    print("colonne latitude et longitutde arrondie ajoute")
    dataframe_copy['latitude'] = dataframe_copy['latitude'].round(size)
    dataframe_copy['longitude'] = dataframe_copy['longitude'].round(size)
    print("arrondi dans dataframe copy mrigl")
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

def supp_sep(df):
    df.loc[df.index % 4 ==0,'id'] = "DEL"
    return df

def modify(df):
    df[df['id'] == 'DEL', 'date'] = '2015-03-09 16:50:00'
    df.loc[['id'] == 'DEL', 'longitude'] = 4.370238
    df.loc[df['id'] == 'DEL', 'latitude'] = 48.870171
    return df

def pertubation2(dataframe):
    dataframe['latitude'] = dataframe['latitude'].round(4) + 0.00044
    dataframe['longitude'] = dataframe['longitude'].round(4) +0.00044
    
    return dataframe