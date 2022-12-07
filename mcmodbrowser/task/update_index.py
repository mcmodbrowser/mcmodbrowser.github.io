import requests
import datetime
from mcmodbrowser.util import loadJson, writeJson, getCurseToken
from mcmodbrowser.model.curse import getCurseHeaders
from mcmodbrowser.index import writeCurseModToIndex, getCurseModLastModifiedTimestamp

def run():
    curseToken = getCurseToken()

    index = loadJson("data/index.json")

    interruptSearch = False
    
    print("Fetching mods since", datetime.datetime.utcfromtimestamp(index['cursors']['curse']).isoformat())

    for searchIndex in range(0, 10000, 50):
        if interruptSearch:
            break
        
        resp = requests.get("https://api.curseforge.com/v1/mods/search?gameId=432&sortField=3&sortOrder=desc&pageSize=50&index={}".format(searchIndex), headers = getCurseHeaders(curseToken))
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            first = True
            for mod in resp.json()["data"]:
                lastModified = getCurseModLastModifiedTimestamp(mod)
                
                if first:
                    print("Search index:", searchIndex, "First mod:", datetime.datetime.utcfromtimestamp(lastModified).isoformat())
                
                if lastModified < index['cursors']['curse']:
                    interruptSearch = True
                    break
                    
                writeCurseModToIndex(index, mod)
                
                first = False
        else:
            print("ERROR: got status code", resp.status_code)
            break
        
    writeJson(index, "data/index.json")
