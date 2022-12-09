import requests
import dateutil.parser as dp
import datetime

from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run(args=[]):
    '''Fetch fileId -> date mappings for use in interpolation.
    
    The Curse API doesn't tell us the modification dates of files when fetching
    mod info in bulk, but it does tell us the file IDs which are allocated
    sequentially. So we fetch the dates of some file IDs, and interpolate
    between them to approximate the modification date of any file ID.
    '''
    
    requestLimit = int(args[args.index("--request-limit") + 1]) if "--request-limit" in args else -1

    curseToken = getCurseToken()

    outFile = "data/curseFileDates.json"
    
    i = 0
    mapping = {'data': {}}
    
    if os.path.exists(outFile):
        mapping = loadJson(outFile)
        i = (max([int(x) for x in mapping["data"].keys()]) // 100000) + 0

    emptyCombo = 0
    fetched = 0
    requestCount = 0

    while True:
        print("Fetching {}XXX00".format(i))
        data = {"fileIds": [x * 100 for x in list(range(i * 1000, (i+1) * 1000))]}
        
        resp = requests.post("https://api.curseforge.com/v1/mods/files", json = data, headers = getCurseHeaders(curseToken))
        requestCount += 1
        
        if requestLimit != -1 and requestCount > requestLimit:
            print("Reached request limit, aborting")
            break
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            if not resp.json()['data']:
                emptyCombo += 1
                
                if emptyCombo > 30:
                    print("Got 30 empty responses in a row, terminating.")
                    break
            
            fetched += len(resp.json()['data'])
            
            for file in resp.json()['data']:
                mapping['data'][file['id']] = dp.isoparse(file['fileDate']).timestamp()
        else:
            print("ERROR: got status code", resp.status_code)
            break
        
        i += 1
    
    print("Fetched", fetched, "values")

    mapping["lastModified"] = epochNow()

    writeJson(mapping, outFile)
