import pandas as pd
import json
from math import sqrt

def lire_fichier(path):
    dataframe = pd.read_csv(path, sep="\t", header=None)
    dataframe.columns = ['QId', 'Date', 'longitude', 'latitude']
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe['week'] = dataframe['Date'].dt.strftime('%Y-%W')
    return dataframe

def sauvegarder_fichiers_par_semaine(dataframe, dossier, prefixe):
    for week in dataframe['week'].unique():
        dataframe[dataframe['week'] == week].to_csv(f'{dossier}/week_{week}.csv', header=False, index=False, sep='\t')

def creer_liste_semaines(dataframe):
    return dataframe['week'].unique()

def creer_guesses_reidentification(ids, weeks, path_origine, path_anonyme):
    guesses_reident = {}

    for id in ids:
        guesses_reident[str(id)] = {}

        for week in weeks:
            df_originale_week = pd.read_csv(f'{path_origine}/week_{week}.csv', sep='\t', names=["Id", "Date", "longitude", "latitude"]).set_index('Date')
            df_anonym_week = pd.read_csv(f'{path_anonyme}/week_{week}.csv', sep='\t', names=["pseudo_Id", "Date", "longitude", "latitude"]).set_index('Date')
            nb_lignes_supp = len(df_originale_week) - len(df_anonym_week)

            df_originale_week = df_originale_week.groupby(['Id'])[['latitude', 'longitude']].aggregate(['count', 'mean']).reset_index()
            df_anonym_week = df_anonym_week.groupby(['pseudo_Id'])[['latitude', 'longitude']].aggregate(['count', 'mean']).reset_index()

            guesses_reident[str(id)][str(week)] = []

            if nb_lignes_supp == 0:
                for index, row in df_originale_week.iterrows():
                    for index1, row1 in df_anonym_week.iterrows():
                        if df_originale_week['latitude']['count'][index] == df_anonym_week['latitude']['count'][index1]:
                            guesses_reident[str(df_originale_week['Id'][index])][week].append(str(df_anonym_week['pseudo_Id'][index1]))
            else:
                for index, row in df_originale_week.iterrows():
                    dist_gps = {}
                    dist_gps[str(df_originale_week['Id'][index])] = []
                    I = str(df_originale_week['Id'][index])
                    pseudo_ids = []
                    for index1, row1 in df_anonym_week.iterrows():
                        if (df_originale_week['latitude']['count'][index] >= df_anonym_week['latitude']['count'][index1] and df_originale_week['latitude']['count'][index] <= df_anonym_week['latitude']['count'][index1] + nb_lignes_supp):
                            dist_gps[I].append(sqrt((df_originale_week['latitude']['mean'][index] - df_anonym_week['latitude']['mean'][index1])**2 + (df_originale_week['longitude']['mean'][index] - df_anonym_week['longitude']['mean'][index1])**2))
                            pseudo_ids.append(str(df_anonym_week['pseudo_Id'][index1]))
                    df = pd.DataFrame.from_dict(dist_gps, orient='index', columns=pseudo_ids)
                    df = df.transpose()
                    ordered = df.nsmallest(1, I)
                    guesses_list = ordered.index.tolist()
                    guesses_reident[str(df_originale_week['Id'][index])][week].extend(guesses_list)

    return guesses_reident

# Fonction pour générer le fichier JSON
def generer_fichier_json(guesses, json_file):
    with open(json_file, 'w') as f:
        json.dump(guesses, f)



def generer_fichier_json(guesses, json_file):
    with open(json_file, 'w') as f:
        json.dump(guesses, f)



if __name__ == "__main__":

    path_originale = "c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"
    path_anonymisee = "S_user_81_8ec0be4582aef1c7a1dc09a40c9f6eccbbed5baa731bc4d4bfaa48214a096d14"
    json_guesses = "strawhat567.json"

   
    df_anonym = lire_fichier(path_anonymisee)
    df_originale = lire_fichier(path_originale)

    sauvegarder_fichiers_par_semaine(df_originale, './fichiers_weeks_orig', 'week')
    sauvegarder_fichiers_par_semaine(df_anonym, './fichiers_weeks_ano', 'week')
    weeks = creer_liste_semaines(df_originale)
    ids = df_originale['Id'].unique()
    guesses_reident = creer_guesses_reidentification(ids, weeks, './fichiers_weeks_orig', './fichiers_weeks_ano')
    generer_fichier_json(guesses_reident, json_guesses)

