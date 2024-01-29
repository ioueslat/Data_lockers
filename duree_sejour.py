def calculer_duree_sejour_lieux_frequents(data, n_lieux=100):
    data = data.copy()
    data['longitude'] = data['longitude'].round(5)
    data['lattitude'] = data['lattitude'].round(5)
    data['lieu'] = list(zip(data['longitude'], data['lattitude']))
    lieux_frequents = data['lieu'].value_counts().index[:n_lieux]

    durees_moyennes = {}
    for lieu in lieux_frequents:
        print(f"Calcul pour le lieu {lieu}")
        donnees_lieu = data[data['lieu'] == lieu]
        durees = []
        for id, group_id in donnees_lieu.groupby('Id'):
            durees.extend(calculer_duree_sejour(group_id))  
        duree_moyenne = np.mean(durees) if durees else 0
        durees_moyennes[lieu] = duree_moyenne
    print(durees_moyennes)
    return durees_moyennes



def calculer_duree_sejour(donnees_id):

    donnees_id = donnees_id.sort_values(by='Date')
    debut_sejour = donnees_id.iloc[0]['Date']
    durees = []
    for i in range(1, len(donnees_id)):
        if (donnees_id.iloc[i]['Date'] - donnees_id.iloc[i-1]['Date']).total_seconds() > 3600:
            fin_sejour = donnees_id.iloc[i-1]['Date']
            duree = (fin_sejour - debut_sejour).total_seconds() / 3600
            durees.append(duree)
            debut_sejour = donnees_id.iloc[i]['Date']
    fin_sejour = donnees_id.iloc[-1]['Date']
    duree = (fin_sejour - debut_sejour).total_seconds() / 3600
    durees.append(duree)

    return durees


def calculer_score_utilite(durees_moyennes_orig,durees_moyennes_anon):
    scores_utilite = []
    for lieu, duree_moyenne_orig in durees_moyennes_orig.items():
        duree_moyenne_anon = durees_moyennes_anon.get(lieu, 0) 
        score_utilite = 1 - min(abs(duree_moyenne_orig - duree_moyenne_anon) / duree_moyenne_orig, 1)
        scores_utilite.append(score_utilite)
    score_utilite_global = np.mean(scores_utilite)
    return score_utilite_global


