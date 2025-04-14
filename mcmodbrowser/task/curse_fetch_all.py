import requests
import time
import sys

from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run(args=[]):
    '''Fetch data of ALL the addons, and put the results in the index.'''
    
    requestLimit = int(args[args.index("--request-limit") + 1]) if "--request-limit" in args else -1
    ATTEMPTS = 3
    
    i = 0
    
    curseToken = getCurseToken()
    
    index = getOrCreateIndex()
    
    maxModifiedTimestamp = 0
    requestCount = 0
    fetched = 0
    missCombo = 0
    
    stop = False

    while True:
        success = False
        for attempt in range(ATTEMPTS):
            print("Fetching {}XXX".format(i))
            sys.stdout.flush()
            data = {"modIds": list(range(i * 1000, (i+1) * 1000))}
            
            resp = requests.post("https://api.curseforge.com/v1/mods", json = data, headers = getCurseHeaders(curseToken))
            requestCount += 1
            time.sleep(0.5)
            
            if requestLimit != -1 and requestCount > requestLimit:
                print("Reached request limit, aborting")
                stop = True
                break
            
            if resp.status_code == 200:
                assert "data" in resp.json()
                
                if resp.json()["data"]:
                    missCombo = 0
                    for mod in resp.json()["data"]:
                        if writeCurseModToIndex(index, mod):
                            fetched += 1
                            
                            ts = getCurseModLastModifiedTimestamp(mod)
                            if ts > maxModifiedTimestamp:
                                maxModifiedTimestamp = ts
                else:
                    missCombo += 1
                    
                    if missCombo >= 300:
                        print("Got 300 empty responses in a row, aborting")
                        stop = True
                        break
                success = True
                break
            else:
                print("ERROR: got status code", resp.status_code)
                if resp.status_code == 502:
                    sleep_mins = (2**attempt)*10
                    how_many_more = ATTEMPTS - attempt - 1
                    if how_many_more > 0:
                        print(f"Retrying {how_many_more} more time{'s' if how_many_more != 1 else ''} after sleeping {sleep_mins} minutes...")
                        time.sleep(sleep_mins * 60)
                else:
                    stop = True
                    break
        
        if not success:
            sys.exit(f"Failed {ATTEMPTS} times in a row")
        if stop:
            break
        
        i += 1
    
    # I don't trust the Curse API to be consistent between endpoints, set cursor
    # back by 3 days to make sure we grab everything
    dictGetWithCreate(index, "cursors")["curse"] = max(0, maxModifiedTimestamp - 60 * 60 * 24 * 3)

    index['lastModified'] = epochNow()
    
    print("Updated", fetched, "mods")
    
    print("Saving index...")
    
    saveIndex(index)
