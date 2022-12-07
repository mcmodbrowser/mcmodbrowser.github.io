import json
import os
from tqdm import tqdm
import dateutil.parser as dp

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

def addonClassIdToType(classId):
    m = {
        17: "worlds",
        5: "bukkitPlugins",
        4546: "customizations",
        4471: "modpacks",
        12: "resourcePacks",
        4559: "addons",
        6: "mods"
    }
    
    return m.get(classId)

def convertModLoader(modLoader):
    m = {
        0: 'any',
        1: 'forge',
        2: 'cauldron',
        3: 'liteloader',
        4: 'fabric',
        5: 'quilt'
    }
    
    if modLoader == None:
        return 'unknown'
    
    return m[modLoader]

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
                if mod["gameId"] != 432:
                    # Not a Minecraft addon
                    continue
                if mod["status"] != 4:
                    # Not approved
                    continue
                
                addonType = addonClassIdToType(mod["classId"])
                
                versions = {}
                
                for ver in mod["latestFilesIndexes"]:
                    verData = versions.get(ver["gameVersion"]) or {}
                    modLoader = convertModLoader(ver["modLoader"])
                    verData[modLoader] = {"fileId": ver["fileId"]}
                    versions[ver["gameVersion"]] = verData
                
                if not versions:
                    # Mod has no files, probably junk
                    continue
                
                modifiedTimestamp = dp.isoparse(mod['dateModified']).timestamp()
                if modifiedTimestamp > maxModifiedTimestamp:
                    maxModifiedTimestamp = modifiedTimestamp
                
                outMod = {
                    "name": mod["name"],
                    "desc": mod["summary"],
                    "authors": [author["name"] for author in mod["authors"]],
                    "downloads": mod["downloadCount"],
                    "url": mod["links"]["websiteUrl"],
                    "versions": versions
                }
                
                slug = mod["slug"]
                
                if not addonType in outData["data"]:
                    outData["data"][addonType] = {}
                if not slug in outData["data"][addonType]:
                    outData["data"][addonType][slug] = {}
                
                outData["data"][addonType][slug]["curse"] = outMod        
            
        else:
            break
        
        i += 1
        
        pb.update()

outData["cursors"]["curse"] = maxModifiedTimestamp

with open("data/index.json", "w", encoding="utf8") as fp:
    json.dump(outData, fp)
