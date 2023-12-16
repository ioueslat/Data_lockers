import pandas as pd
import json

def fichierparsemaine(path_originale, path_anonymisee,chemin_dossierOrig,chemin_dossierAno,chemin_resultat):
   
    dfA = pd.read_csv(path_anonymisee, sep="\t", header=None)
    dfA.columns = ['AId', 'Date', 'longitude', 'latitude']
    dfA = dfA[dfA['AId'] != 'DEL']
    dfA['Date'] = pd.to_datetime(dfA['Date'], errors='coerce', dayfirst=True)
    dfA['week'] = dfA['Date'].dt.strftime('%Y-%W')

    dfO = pd.read_csv(path_originale, sep="\t", header=None)
    dfO.columns = ['Id', 'Date', 'longitude', 'latitude']
    dfO['Date'] = pd.to_datetime(dfO['Date'], errors='coerce', dayfirst=True)
    dfO['week'] = dfO['Date'].dt.strftime('%Y-%W')

    for week in dfO['week'].unique():
        dfO[dfO['week'] == week].to_csv(f'{chemin_dossierOrig}/week_{week}.csv', header=False, index=False, sep='\t')
        dfA[dfA['week'] == week].to_csv(f'{chemin_dossierAno}week_{week}.csv', header=False, index=False, sep='\t')
    weeks = dfO['week'].unique()

    ids = dfO['Id'].unique()
    return weeks, ids

def guesses(weeks, ids,chemin_dossierOrig, chemin_dossierAno,chemin_resultat ):
    guesses = {}

    for id in ids:
        guesses[str(id)] = {}
        for week in weeks:
            guesses[str(id)][str(week)] = None 

    for week in weeks:
        dfO_week = pd.read_csv(f'{chemin_dossierOrig}/week_{week}.csv', sep='\t', names=["Id", "Date", "longitude", "latitude", "week"]).set_index('Date')
        dfA_week = pd.read_csv(f'{chemin_dossierAno}/week_{week}.csv', sep='\t', names=["pseudo_Id", "Date",  "longitude","latitude", "week"]).set_index('Date')

        dfO_week['latitude'] = dfO_week['latitude'].round(2)
        dfO_week['longitude'] = dfO_week['longitude'].round(2)
        merged_df = dfA_week.merge(dfO_week, how='inner', on=['Date', 'latitude', 'longitude']).set_index('Id')
        merged_df = merged_df.drop(columns=['latitude', 'longitude'])
        guessm = merged_df.groupby(['Id', 'pseudo_Id']).count().reset_index()
        guessm['pseudo_Id'] = guessm['pseudo_Id'].astype('str')

        for id in ids:
            common_pseudo_id = guessm[guessm['Id'] == id]['pseudo_Id'].mode()
            if not common_pseudo_id.empty:
                common_pseudo_id = common_pseudo_id[0] 
                if isinstance(common_pseudo_id, str):
                    common_pseudo_id = [common_pseudo_id]  
                guesses[str(id)][str(week)] = common_pseudo_id
            else:
                guesses[str(id)][str(week)] = None

    jsonn = f'{chemin_resultat}/resultat.json'

    with open(jsonn, 'w') as f:
        json.dump(guesses, f, indent=4)



if __name__ == "__main__":
    path_originale = "fichier_originale"
    path_anonymisee = "fichieranony"
    chemin_dossierOrig = "./fichiers_orig"
    chemin_dossierAno = "./fichiers_ano"
    chemin_resultat = "/reidentification_resultat"

    weeks, ids = fichierparsemaine(path_originale, path_anonymisee, chemin_dossierOrig, chemin_dossierAno, chemin_resultat)
    guesses(weeks, ids, chemin_dossierOrig, chemin_dossierAno, chemin_resultat)