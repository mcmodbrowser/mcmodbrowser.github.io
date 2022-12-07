import requests
import datetime

from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run():
    '''Fetch dump of ALL the addons, and put the results in the index.'''
    
    i = 0
    
    index = getOrCreateIndex()
    
    maxModifiedTimestamp = 0
    fetched = 0

    while True:
        print("Fetching {}XXX".format(i))
        
        filename = "data/dump/curse_all/mods-{}k.json".format(i)
        
        if os.path.exists(filename):
            respJson = loadJson(filename)
        else:
            break
        
        assert "data" in respJson
        
        for mod in respJson["data"]:
            if writeCurseModToIndex(index, mod):
                fetched += 1
                
                ts = getCurseModLastModifiedTimestamp(mod)
                if ts > maxModifiedTimestamp:
                    maxModifiedTimestamp = ts
        
        i += 1
    
    dictGetWithCreate(index, "cursors")["curse"] = maxModifiedTimestamp

    index['lastModified'] = datetime.datetime.utcnow().timestamp()
    
    print("Updated", fetched, "mods")
    
    print("Saving index...")
    
    saveIndex(index)
