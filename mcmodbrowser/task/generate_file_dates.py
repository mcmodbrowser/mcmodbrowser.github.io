import requests
import json
import os
import sys
import dateutil.parser as dp
import datetime

def run():

    i = 0

    if 'CURSEFORGE_TOKEN' not in os.environ:
        sys.exit("You must set the CURSEFORGE_TOKEN environmental variable to your CurseForge API key.")

    os.makedirs("data/response", exist_ok=True)

    mapping = {}

    emptyCombo = 0

    while True:
        data = {"fileIds": [x * 1000 for x in list(range(i * 1000, (i+1) * 1000))]}
        
        resp = requests.post("https://api.curseforge.com/v1/mods/files", json = data, headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'x-api-key': os.environ['CURSEFORGE_TOKEN']})
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            if not resp.json()['data']:
                emptyCombo += 1
                
                if emptyCombo > 3:
                    print("Got three empty responses in a row, terminating.")
                    break
            
            for file in resp.json()['data']:
                mapping[file['id']] = dp.isoparse(file['fileDate']).timestamp()
        else:
            print("ERROR: got status code", resp.status_code)
            break
        
        i += 1

    with open("data/fileDates.json".format(i), "w", encoding="utf8") as fp:
        json.dump({"data": mapping, "timestamp":  datetime.datetime.utcnow().isoformat()}, fp)
