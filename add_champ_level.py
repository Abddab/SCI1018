import requests
import pandas as pd
import time

# Lire le fichier CSV en tant que DataFrame pandas.
df = pd.read_csv('League_data_SCI1018.csv')

api_endpoint = 'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/'
api_key = 'RGAPI-0a95f8c5-2bf8-4502-9fc4-2a1868427488'

champion_levels = []

# Parcourir chaque ligne du DataFrame.
for index, row in df.iterrows():

  summoner_id = row['summonerId']
  champion_id = row['championId']
  
  # Définir l'URL de l'API en utilisant l'ID invocateur et l'ID champion.
  api_url = f'{api_endpoint}{summoner_id}/by-champion/{champion_id}'
  
  # Faire la requête à l'API
  response = requests.get(api_url, headers={'X-Riot-Token': api_key})
  
  # Vérifier si la requête a été ratée en raison de la limite de taux.
  while response.status_code == 429:
    print('Waiting due to rate limiting...')
    time.sleep(130)
    
    # Faire la requête à l'API
    response = requests.get(api_url, headers={'X-Riot-Token': api_key})
  
  # Vérifier si la requête a réussi
  if response.status_code == 200:

    champion_level = response.json()['championLevel']
    
    champion_levels.append(champion_level)
  else:

    champion_levels.append(None)

# Ajouter une nouvelle colonne au DataFrame avec les niveaux de champion.
df['ChampionLevel'] = champion_levels

# Écrire le DataFrame dans un nouveau fichier CSV.
df.to_csv('League_data_SCI1018_updated3.csv', index=False)