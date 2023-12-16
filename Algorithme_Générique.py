import pandas as pd
import csv
import json
import math
from math import sqrt, radians, sin, cos, sqrt, asin
import datetime


# Distances

def distance_euclidienne(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
def distance_manhattan(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
def haversine_distance(point1, point2):

    lat1 = point1[0]
    lon1 = point1[1]
    lat2 = point2[0]
    lon2 = point2[1]
    
    # Convertir les latitudes et longitudes de degrés à radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Calculer les différences de latitude et de longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Formule haversine
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Rayon moyen de la Terre en kilomètres
    distance = r * c
    
    return distance


def lire_fichier_orig(path_originale):
    df_orig = pd.read_csv(path_originale, sep="\t", header=None).set_axis(['Id', 'Date', 'longitude', 'latitude'], axis=1)
    df_orig['Date'] = pd.to_datetime(df_orig['Date'])
    df_orig['Semaine'] = df_orig['Date'].dt.strftime('%G-%V')
    return df_orig

def lire_fichier_anony(path_anonym):
    df_ano = pd.read_csv(path_anonym, sep="\t", header=None).set_axis(['Id_Ano', 'Date', 'longitude', 'latitude'], axis=1)
    df_ano = df_anonym[df_ano['Id_Ano'] != 'DEL'].dropna()
    df_ano['Date'] = pd.to_datetime(df_ano['Date'])
    df_ano['Semaine'] = df_ano['Date'].dt.strftime('%G-%V')
    return df_ano

def sauvegarder_fichiers_par_semaine(df_orig, df_ano, Semaines, chemin_dossierOrig, chemin_dossierAno):
    for semaine in Semaines:
        df_orig[df_orig['Semaine'] == semaine].to_csv(f'{chemin_dossierOrig}/Semaine_{semaine}.csv', header=False, index=False, sep='\t')
        df_ano[df_ano['Semaine'] == semaine].to_csv(f'{chemin_dossierAno}/Semaine_{semaine}.csv', header=False, index=False, sep='\t')

        
def creer_guesses_reidentification(Semaines, id_set,chemin_dossierOrig, chemin_dossierAno):
    guesses = {}

    for id in id_set:
        guesses[str(id)] = {}
    
    for semaine in Semaines:
        
        df_orig_Sem = pd.read_csv(f'{chemin_dossierOrig}/Semaine{semaine}.csv', sep='\t', names=["Id", "date", "latitude", "longitude", "semaine"]).set_index('date')
        df_ano_Sem = pd.read_csv(f'{chemin_dossierAno}/Semaine{semaine}.csv', sep='\t', names=["Id_Ano", "date", "latitude", "longitude", "semaine"]).set_index('date')
        #calcule de différence des lignes 
        diff_lignes_Del = len(df_orig_Sem) - len(df_ano_Sem)
        
        df_orig_Sem = df_orig_Sem.groupby(['Id'])[['latitude', 'longitude']].aggregate(['count', 'mean']).reset_index()
        df_ano_Sem = df_ano_Sem.groupby(['Id_Ano'])[['latitude', 'longitude']].aggregate(['count', 'mean']).reset_index()

        for id in id_set:
            if str(id) not in guesses:
                guesses[str(id)] = {}
            guesses[str(id)][str(semaine)] = []
            
        
        if diff_lignes_Del == 0:

            for i, _ in df_orig_Sem.iterrows():
                for j, _ in df_ano_Sem.iterrows():
                    if df_orig_Sem['latitude']['count'][i] == df_ano_Sem['latitude']['count'][j]:
                        guesses[str(df_orig_Sem['Id'][i])][semaine].append(str(df_ano_Sem['Id_Ano'][j]))
        else:
            
            for i, _ in df_orig_Sem.iterrows():

                    # Initialisation des structures de données
                distances = {}
                distances[str(df_orig_Sem['Id'][i])] = []
                
                S = df_orig_Sem['Id'][i].astype(str)
                
                Id_Ano_List = []

                for j, _ in df_ano_Sem.iterrows():
                    
                    if (df_orig_Sem['latitude']['count'][i] >= df_ano_Sem['latitude']['count'][j] and df_orig_Sem['latitude']['count'][i] <= df_ano_Sem['latitude']['count'][j] + diff_lignes_Del):

                    # Calcul de la distance entre les données
                        distances[S].append(distance_euclidienne((df_orig_Sem['latitude']['mean'][i],df_orig_Sem['longitude']['mean'][i]),(df_ano_Sem['latitude']['mean'][j], df_ano_Sem['longitude']['mean'][j])))
                        Id_Ano_List.append(df_ano_Sem['Id_Ano'][j].astype(str))

                    # Création d'un DataFrame à partir des distances calculées
                df = pd.DataFrame.from_dict(distances, orient='index', columns=Id_Ano_List)
                df = df.transpose()

                    # Trouver la plus petite distance pour obtenir la liste des prédictionsi
                ordered = df.nsmallest(1, S)
                guesses_List = ordered.index.tolist()
                guesses[str(df_orig_Sem['id'][i])][semaine].extend(guesses_List)    

    return guesses


def generer_fichier_json(guesses, json_file):
    with open(json_file, 'w') as f:
        json.dump(guesses, f,indent=4)

if __name__ == "__main__":
    #Les chemins
    path_originale = "fichier_originale"
    path_anonymisee = "fichier_anononymisé"
    json_guesses = "Résultat.json"
    orig_folder_path = "./fichiers_orig" 
    anon_folder_path = "./fichiers_ano"
    # Lecture des données
    df_originale = lire_fichier_orig(path_originale)
    df_anonym = lire_fichier_anony(path_anonymisee)
    #Extraction de l'ensemble de smmaine et l'ensemble des identifiants 
    semaines = df_originale['semaine'].unique()
    ids = df_originale['Id'].unique()
    #Séparation des données par semaine
    sauvegarder_fichiers_par_semaine(df_originale,df_anonym,semaines,orig_folder_path,anon_folder_path)

    df_originale = df_originale.drop(columns=['semaine'])
    df_anonym = df_anonym.drop(columns=['semaine'])
    #Création de suppositions pour la réidentification des individus : 
    guesses = creer_guesses_reidentification(semaines, ids,orig_folder_path,anon_folder_path)