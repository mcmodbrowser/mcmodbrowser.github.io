import dateutil.parser as dp
import os
from mcmodbrowser.util import *

def getIndexPath():
    return "data/index.json"

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
    
    return m.get(classId) or f"unmapped-curse-class-{classId}"

def convertModLoader(modLoader):
    m = {
        0: 'any',
        1: 'forge',
        2: 'cauldron',
        3: 'liteloader',
        4: 'fabric',
        5: 'quilt',
        6: 'neoforge',
    }
    
    if modLoader == None:
        return 'none'
    
    return m.get(modLoader) or f"unmapped-curse-loader-{modLoader}"

def writeCurseModToIndex(index, mod):
    '''Returns true if something was written to the index.'''
    if mod["gameId"] != 432:
        # Not a Minecraft addon
        return False
    if mod["status"] != 4:
        # Not approved
        return False
    
    addonType = addonClassIdToType(mod["classId"])
    
    versions = {}
    
    for ver in mod["latestFilesIndexes"]:
        verData = versions.get(ver["gameVersion"]) or {}
        modLoader = convertModLoader(ver.get("modLoader"))
        if modLoader not in verData or verData[modLoader]['fileId'] < ver['fileId']:
            verData[modLoader] = {"fileId": ver["fileId"]}
        versions[ver["gameVersion"]] = verData
    
    if not versions:
        # Mod has no files, probably junk
        return False
    
    outMod = {
        "name": mod["name"],
        "desc": mod["summary"],
        "authors": [author["name"] for author in mod["authors"]],
        "downloads": mod["downloadCount"],
        "url": mod["links"]["websiteUrl"],
        "versions": versions
    }
    
    slug = mod["slug"]
    
    dictGetWithCreate(index, "data", addonType, slug)["curse"] = outMod
    
    index["data"][addonType][slug]["curse"] = outMod
    
    return True

def getCurseModLastModifiedTimestamp(mod):
    return dp.isoparse(mod['dateModified']).timestamp()

def getOrCreateIndex():
    if os.path.exists(getIndexPath()):
        return loadJson(getIndexPath())
    else:
        return {
            "data": {},
            "version": 0,
        }

def saveIndex(index):
    writeJson(index, getIndexPath())
