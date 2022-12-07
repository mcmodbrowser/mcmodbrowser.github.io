import requests

from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run():
    '''Fetch data of ALL the addons, and put the results in the index.'''
    
    i = 0
    
    curseToken = getCurseToken()
    
    index = getOrCreateIndex()
    
    maxModifiedTimestamp = 0

    while True:
        data = {"modIds": list(range(i * 1000, (i+1) * 1000))}
        
        resp = requests.post("https://api.curseforge.com/v1/mods", json = data, headers = getCurseHeaders(curseToken))
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            for mod in resp.json()["data"]:
                if writeCurseModToIndex(index, mod):
                    ts = getCurseModLastModifiedTimestamp(mod)
                    if ts > maxModifiedTimestamp:
                        maxModifiedTimestamp = ts
        else:
            print("ERROR: got status code", resp.status_code)
            break
        
        i += 1
    
    
    dictGetWithCreate(index, "cursors")["curse"] = maxModifiedTimestamp

    saveIndex(index)
