import json
import random
import time
import requests
import pandas as pd

from enum import IntEnum

class GameConstants(IntEnum):
    NUMBER_OF_PLAYERS_IN_A_GAME = 10
    NUMBER_OF_MATCHES = 5
    PLAYERS_TO_FETCH = 5000



# Attribuez la clé de développement située dans 'api_key.txt' à api_key.
f = open('api_key.txt','r')
api_key = f.read()
f.close()

keyParams = '?api_key=' + api_key

def getSummoner(summonerName: str, field: str):
    """
    Récupère les informations d'un invocateur en fonction d'un champ spécifique. Il est utilisé pour récupérer les données de match d'un invocateur dans un autre appel API.

    Paramètres:
    summonerName (str): Le nom de l'invocateur.
    field (str): Le champ que vous voulez obtenir. Par exemple, le 'puuid' de l'invocateur.
    """
    params = keyParams
    summonerNameURL = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}" + params
    resp = requests.get(summonerNameURL)
    summonerInfo = resp.json()[field]
    return summonerInfo
    

def getRankedMatchList(summonerPuuid: str, count: int = 20):
    """
    Renvoie une liste d'ID de match classés. Il est utilisé en tant qu'entrée pour récupérer les détails de chaque match dans un autre appel API.

    Paramètres:
    summonerPuuid (str): le puuid de l'invocateur
    count (str): le nombre de matchs à renvoyer entre '0' et '100'. Par défaut à 20.

    """
    params = keyParams + f'&type=ranked&count={str(count)}'
    summonerMatchListURL = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerPuuid}/ids" + params
    timeCounter = 0
    while True:
        resp = requests.get(summonerMatchListURL)
        print(resp.status_code)
        if resp.status_code == 429:
            print("Waiting 130 seconds for API rate limit..." + f"{timeCounter} seconds elapsed")
            time.sleep(10)
            timeCounter+=10
            continue
        summonerMatchList = resp.json()
        return summonerMatchList


def getMatchData(match: str):
    """
    Récupère les données d'un match.
    """
    params = keyParams
    matchDataURL = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match}' + params
    timeCounter = 0
    while True:
        resp = requests.get(matchDataURL)
        print(resp.status_code)
        if resp.status_code == 429:
            print("Waiting 130 seconds for API rate limit..." + f"{timeCounter} seconds elapsed")
            time.sleep(10)
            timeCounter+=10
            continue
        matchData = resp.json()
            
        return matchData

def loadData(matchData: dict, df: pd.core.frame.DataFrame):
    """
    Charge les données de match (qui contiennent 10 joueurs) dans le dataframe df fourni.
    """
    for participant in range(GameConstants.NUMBER_OF_PLAYERS_IN_A_GAME):
            player_data = matchData['info']['participants'][participant]

            list = [
                    player_data['puuid'],player_data['summonerId'], player_data['championId'],
                    player_data['championName'], player_data['win']
                   ]
                    
            
            df.loc[0] = list
            df.index = df.index + 1

    return None

def getChampionMastery(championId: int, summonerId: str, field: str):
    """
    Récupère les détails d'un invocateur sur leur maîtrise d'un certain champion.

    Paramètres:
    championId (int): L'ID du champion
    summonerId (str): L'ID invocateur chiffré
    field (str): Le champ que vous voulez obtenir. Par exemple, le 'championLevel'
    """
    params = keyParams
    championMasteryURL = f'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/by-champion/{championId}' + params
    resp = requests.get(championMasteryURL)
    masteryData = resp.json()[field]

    return masteryData

def selectRandomPlayer(puuid: list):
    """
    Sélectionne le puuid d'un invocateur au hasard dans une liste fournie de puuids d'invocateurs
    """
    return random.choice(puuid)


"""
L'EXÉCUTION DU CODE COMMENCE ICI
"""

id = 'dhAJ9HbAox7FewEaIlN28yWB8LTZbisT67wGZQ1c1Pi3r2GiU7vqvv6DDIIqrshpkP-gogZL4JhGug' 

fetched_players_count = 0

# Tant que nous n'avons pas récupéré les données de match pour le nombre de joueurs COUNT_OF_PLAYERS_TO_FETCH, continuer à boucler.
while fetched_players_count < 5000:
    
    # Réinitialise le contenu des dataframes à vide.
    df_matchData = pd.DataFrame(columns = ['puuid','summonerId', 'championId','championName', 'win'])

    df_fetchedPlayers = pd.DataFrame(columns = ['puuid'])
    

    # Récupère la liste de matchs du joueur et récupère les données de 5 matchs. Notez qu'il y a 10 joueurs dans chaque match.
    matchlist = getRankedMatchList(id, 5)

    for match in matchlist:
        matchData = getMatchData(match)
        loadData(matchData, df_matchData)



    #Une fois les données d'un joueur récupérées, sélectionnez un nouveau joueur au hasard dans la liste de matchs
    #du joueur précédent
    id = selectRandomPlayer(df_matchData['puuid'].unique().tolist()) 
    df_matchData.to_csv('LoL_Match_Data.csv', header = False, index = False, mode = 'a')
    
    fetched_players_count += 1











