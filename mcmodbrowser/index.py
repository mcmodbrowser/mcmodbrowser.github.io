import dateutil.parser as dp

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
        modLoader = convertModLoader(ver["modLoader"])
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
    
    if not addonType in index["data"]:
        index["data"][addonType] = {}
    if not slug in index["data"][addonType]:
        index["data"][addonType][slug] = {}
    
    index["data"][addonType][slug]["curse"] = outMod
    
    return True

def getCurseModLastModifiedTimestamp(mod):
    return dp.isoparse(mod['dateModified']).timestamp()
