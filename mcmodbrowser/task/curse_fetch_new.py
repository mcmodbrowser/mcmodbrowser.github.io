import requests
import datetime
from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run(args=[]):
    '''Fetch recently updated mods and put them in the index.'''
    
    requestLimit = int(args[args.index("--request-limit") + 1]) if "--request-limit" in args else -1
    
    curseToken = getCurseToken()

    index = loadJson("data/index.json")

    interruptSearch = False
    
    print("Fetching mods since", datetime.datetime.utcfromtimestamp(index['cursors']['curse']).isoformat(), "(", index['cursors']['curse'], ")")
    
    firstModModificationDate = None
    fetched = 0
    requestCount = 0
    fetchedExtra = 0

    for searchIndex in range(0, 10000, 50):
        if interruptSearch:
            break
        
        resp = requests.get("https://api.curseforge.com/v1/mods/search?gameId=432&sortField=3&sortOrder=desc&pageSize=50&index={}".format(searchIndex), headers = getCurseHeaders(curseToken))
        requestCount += 1
        
        if requestLimit != -1 and requestCount > requestLimit:
            print("Reached request limit, aborting")
            break
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            first = True
            for mod in resp.json()["data"]:
                lastModified = getCurseModLastModifiedTimestamp(mod)
                
                if first:
                    print("Search index:", searchIndex, "First mod:", datetime.datetime.utcfromtimestamp(lastModified).isoformat())
                
                print("  updating:", mod['slug'])
                
                if lastModified < index['cursors']['curse']:
                    # Fetch some redundant entries to cope with unreliable API
                    if fetchedExtra == 0:
                        print("Older than cursor, fetching 30 more")
                    fetchedExtra += 1
                    if fetchedExtra > 30:
                        print("Fetched 30 extra entries, aborting")
                        interruptSearch = True
                        break
                    
                if writeCurseModToIndex(index, mod):
                    fetched += 1
                
                if firstModModificationDate == None:
                    firstModModificationDate = lastModified
                
                first = False
        else:
            print("ERROR: got status code", resp.status_code)
            break
    
    if firstModModificationDate:
        index['cursors']['curse'] = firstModModificationDate
    
    index['lastModified'] = epochNow()
    
    print("Updated", fetched, "mods")
    
    print("Writing index...")
    
    writeJson(index, "data/index.json")
