import requests
import json
import os
import sys

i = 0
# curl -d '@data.json' -H 'Content-Type: application/json'  -H 'Accept: application/json' -H "x-api-key: $API_KEY" -X POST 'https://api.curseforge.com/v1/mods'

if 'CURSEFORGE_TOKEN' not in os.environ:
    sys.exit("You must set the CURSEFORGE_TOKEN environmental variable to your CurseForge API key.")

os.makedirs("data/response", exist_ok=True)

while True:
    data = {"modIds": list(range(i * 1000, (i+1) * 1000))}
    
    resp = requests.post("https://api.curseforge.com/v1/mods", json = data, headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'x-api-key': os.environ['CURSEFORGE_TOKEN']})
    
    if resp.status_code == 200:
        assert "data" in resp.json()
        with open("data/response/mods-{}k.json".format(i), "w", encoding="utf8") as fp:
            json.dump(resp.json(), fp)
    else:
        print("ERROR: got status code", resp.status_code)
        break
    
    i += 1
