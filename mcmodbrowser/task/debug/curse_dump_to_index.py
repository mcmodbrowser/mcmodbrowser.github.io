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
    
    # I don't trust the Curse API to be consistent between endpoints, set cursor
    # back by 3 days to make sure we grab everything
    dictGetWithCreate(index, "cursors")["curse"] = maxModifiedTimestamp - 60 * 60 * 24 * 3

    index['lastModified'] = epochNow()
    
    print("Updated", fetched, "mods")
    
    print("Saving index...")
    
    saveIndex(index)
