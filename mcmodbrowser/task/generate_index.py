import json
import os
from tqdm import tqdm
from mcmodbrowser.index import writeCurseModToIndex

# SCHEMA
'''
data {
    addonType... [
        addonSlug... {
            websiteID... {
                name
                description
                authors [
                    author...
                ]
                downloads
                url
                versions {
                    version... {
                        loader... {
                            lastModified
                        }
                    }
                }
            }
        }
    ]
}

version

cursors {
    websiteID... {
        cursor
    }
}

'''

def run():

    outData = {
        "data": {},
        "version": 0,
        "cursors": {}
    }

    maxModifiedTimestamp = 0

    i = 0
    with tqdm() as pb:
        while True:
            filename = "data/response/mods-{}k.json".format(i)
            
            if os.path.exists(filename):
                data = {}
                with open(filename, "r", encoding="utf8") as fp:
                    data = json.load(fp)
                
                for mod in data["data"]:
                    writeCurseModToIndex(outData, mod)
                
            else:
                break
            
            i += 1
            
            pb.update()

    outData["cursors"]["curse"] = maxModifiedTimestamp

    with open("data/index.json", "w", encoding="utf8") as fp:
        json.dump(outData, fp)
