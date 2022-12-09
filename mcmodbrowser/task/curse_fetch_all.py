import requests
import datetime

from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run(args=[]):
    '''Fetch data of ALL the addons, and put the results in the index.'''
    
    requestLimit = int(args[args.index("--request-limit") + 1]) if "--request-limit" in args else -1
    
    i = 0
    
    curseToken = getCurseToken()
    
    index = getOrCreateIndex()
    
    maxModifiedTimestamp = 0
    requestCount = 0
    fetched = 0

    while True:
        print("Fetching {}XXX".format(i))
        data = {"modIds": list(range(i * 1000, (i+1) * 1000))}
        
        resp = requests.post("https://api.curseforge.com/v1/mods", json = data, headers = getCurseHeaders(curseToken))
        requestCount += 1
        
        if requestLimit != -1 and requestCount > requestLimit:
            print("Reached request limit, aborting")
            break
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            for mod in resp.json()["data"]:
                if writeCurseModToIndex(index, mod):
                    fetched += 1
                    
                    ts = getCurseModLastModifiedTimestamp(mod)
                    if ts > maxModifiedTimestamp:
                        maxModifiedTimestamp = ts
        else:
            print("ERROR: got status code", resp.status_code)
            break
        
        i += 1
    
    # I don't trust the Curse API to be consistent between endpoints, set cursor
    # back by 3 days to make sure we grab everything
    dictGetWithCreate(index, "cursors")["curse"] = maxModifiedTimestamp - 60 * 60 * 24 * 3

    index['lastModified'] = epochNow()
    
    print("Updated", fetched, "mods")
    
    print("Saving index...")
    
    saveIndex(index)
