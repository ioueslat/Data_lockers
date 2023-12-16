import pandas as pd
import json

def Lecture_fichier_ano(chemin_anony):
    df_ano = pd.read_csv(chemin_anony, sep='\t', header=None, names=['Type', 'Date', 'Latitude', 'Longitude'])
    # Filtrage des lignes de DEL 
    df_ano = df_ano[df_ano['Type'] != 'DEL']
    df_ano['Date'] = pd.to_datetime(df_ano['Date'], errors='coerce', dayfirst=True)
    df_ano['week'] = df_ano['Date'].dt.strftime('%G-%V')
    return df_ano

def Lecture_fichier_orig(chemin_orig):
    df_org = pd.read_csv(chemin_orig, sep='\t', header=None, names=['Type', 'Date', 'Latitude', 'Longitude'])
    df_org['Date'] = pd.to_datetime(df_org['Date'], errors='coerce', dayfirst=True)
    df_org['Latitude'] = df_org['Latitude'].round(3)
    df_org['Longitude'] = df_org['Longitude'].round(3)
    return df_org

def fusionner_dataframes(df_ano, df_org):
    merged_df = pd.merge(df_org, df_ano, on=['Date', 'Longitude', 'Latitude'], how='inner')
    df_resultat = merged_df[['id1', 'id2', 'Date', 'Longitude', 'Latitude', 'week1']].drop_duplicates(subset=['id1', 'id2'])
    return df_resultat

def creer_json(df_resultat, chemin_json):
    # Créer un dictionnaire pour stocker les données au format souhaité
    resultat_json = {}
    for index, ligne in df_resultat.iterrows():
        id_original = ligne['id1']
        semaine = f"2015-{ligne['week1']}"
        id_anonymise = ligne['id2']
        if id_original not in resultat_json:
            resultat_json[id_original] = {}
        if semaine not in resultat_json[id_original]:
            resultat_json[id_original][semaine] = []
        resultat_json[id_original][semaine].append(id_anonymise)
    with open(chemin_json, 'w') as fichier_json:
        json.dump(resultat_json, fichier_json, indent=4)

if __name__ == "__main__":
    # Chemins de fichiers
    fichier_anonymise = "fichier_anonymisé.csv"
    fichier_originale = "ichier_org.csv"
    chemin_sortie_json = "resultat.json"

    df_ano = Lecture_fichier_ano(fichier_anonymise)
    df_org = Lecture_fichier_orig(fichier_originale)
    df_fusionne = fusionner_dataframes(df_ano, df_org)
    creer_json(df_fusionne, chemin_sortie_json)
