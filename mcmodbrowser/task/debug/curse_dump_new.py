import requests
import datetime
from mcmodbrowser.util import loadJson, writeJson, getCurseToken
from mcmodbrowser.model.curse import getCurseHeaders
from mcmodbrowser.index import writeCurseModToIndex, getCurseModLastModifiedTimestamp

def run():
    '''Fetch recently updated mods and dump them.'''
    
    curseToken = getCurseToken()

    for searchIndex in range(0, 10000, 50):
        print(searchIndex, "/", 9950)
        resp = requests.get("https://api.curseforge.com/v1/mods/search?gameId=432&sortField=3&sortOrder=desc&pageSize=50&index={}".format(searchIndex), headers = getCurseHeaders(curseToken))
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            writeJson(resp.json(), "data/dump/curse_new/{}.json".format(searchIndex))
        else:
            print("ERROR: got status code", resp.status_code)
            break
    
