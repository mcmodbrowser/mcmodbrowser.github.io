import requests

from mcmodbrowser.index import *
from mcmodbrowser.util import *
from mcmodbrowser.model.curse import *

def run(args=[]):
    '''Fetch data of ALL the addons, and dump them.'''
    
    i = 0
    
    curseToken = getCurseToken()

    while True:
        print("Fetching {}XXX".format(i))
        data = {"modIds": list(range(i * 1000, (i+1) * 1000))}
        
        resp = requests.post("https://api.curseforge.com/v1/mods", json = data, headers = getCurseHeaders(curseToken))
        
        if resp.status_code == 200:
            assert "data" in resp.json()
            
            writeJson(resp.json(), "data/dump/curse_all/mods-{}k.json")
        else:
            print("ERROR: got status code", resp.status_code)
            break
        
        i += 1
    
