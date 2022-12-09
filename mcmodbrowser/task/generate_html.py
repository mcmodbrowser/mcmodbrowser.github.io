import glob
import os
import sys
import shutil
import json
import datetime
from jinja2 import Template
import os
from mcmodbrowser.util import humanizeIsoTimestamp

def run(args=[]):
    '''Generate HTMLs from index.'''

    if False in [os.path.exists(x) for x in [".git", "public_template"]]:
        sys.exit("You must run this script from the root directory of the repo.")

    if os.path.exists("public"):
        shutil.rmtree("public")

    shutil.copytree("public_template", "public")

    def loadJson(path):
        with open(path, "r", encoding="utf8") as fp:
            return json.load(fp)

    index = loadJson("data/index.json")
    
    def lerp_line(x0, y0, x1, y1, x):
        a = (y1 - y0) / (x1 - x0)
        b = y0 - a * x0
        # a*x0+b=y0 => b=y0-a*x0
        
        return a * x + b
    
    FILE_ID_STEP = 100
    
    def loadFileDates():
        fileDates = loadJson("data/fileDates.json")    
        
        fileDatesMapping = {}
        for id, date in fileDates['data'].items():
            fileDatesMapping[int(id)] = date
        fileDatesMappingKeys = sorted([int(x) for x in fileDatesMapping.keys()])
        
        xs = list(range(fileDatesMappingKeys[0], fileDatesMappingKeys[-1] + FILE_ID_STEP, FILE_ID_STEP))
        ys = [0] * len(xs)
        
        gapStart = -1
        
        for i in range(len(xs)):
            x = xs[i]
            
            if x in fileDatesMapping:
                ys[i] = fileDatesMapping[x]
                
                if gapStart != -1:
                    # there is a gap from gapStart to i-1 (both inclusive)
                    
                    x0 = xs[gapStart - 1]
                    y0 = ys[gapStart - 1]
                    x1 = xs[i]
                    y1 = ys[i]
                    
                    for gapI in range(gapStart, i):
                        ys[gapI] = lerp_line(x0, y0, x1, y1, xs[gapI])
                
                gapStart = -1
            elif gapStart == -1:
                gapStart = i
        
        return xs, ys
        
    fileDatesXs, fileDatesYs = loadFileDates()
    

    def fileIdToApproximateEpoch(p):
        '''Linearly interpolate between known fileId -> date mappings.'''
        x0, y0, x1, y1 = (None, None, None, None)
        
        xs = fileDatesXs
        ys = fileDatesYs
        
        if p < xs[0]:
            x0 = xs[0]
            y0 = ys[0]
            x1 = xs[1]
            y1 = ys[1]
        elif p > xs[-1]:
            x0 = xs[-2]
            y0 = ys[-2]
            x1 = xs[-1]
            y1 = ys[-1]
        else:
            x0 = (p // FILE_ID_STEP) * FILE_ID_STEP
            y0 = ys[(x0 - xs[0]) // FILE_ID_STEP]
            x1 = ((p // FILE_ID_STEP) + 1) * FILE_ID_STEP
            y1 = ys[(x1 - xs[0]) // FILE_ID_STEP]
        
        return lerp_line(x0, y0, x1, y1,p)
            
    def fileIdToApproximateDate(p):
        return humanizeIsoTimestamp(datetime.datetime.utcfromtimestamp(fileIdToApproximateEpoch(p)).isoformat())

    def createTemplateEntries(index, addonType, version):
        result = []
        for type in index['data'].keys():
            if addonType != 'index' and type != addonType:
                continue
            
            for slug in index['data'][type]:
                addonMulti = index['data'][type][slug]
                
                addon = addonMulti['curse']
                
                if version != 'index' and not version in addon['versions']:
                    continue
                
                latestFileId = None
                if version != 'index':
                    latestFileId = max(x['fileId'] for x in addon['versions'][version].values())
                else:
                    for ver in addon['versions']:
                        latestFileId = max((latestFileId or 0), max(x['fileId'] for x in addon['versions'][ver].values()))
                
                result.append({
                    'name': addon['name'],
                    'url': addon['url'],
                    'description': addon['desc'],
                    'authors': ', '.join(addon['authors']),
                    'downloads': addon['downloads'],
                    'downloadsFormatted': addon['downloads'],
                    'lastModifiedDefault': fileIdToApproximateDate(latestFileId).replace(" ", "&nbsp")
                })
        
        result = list(reversed(sorted(result, key=lambda addon: addon['lastModifiedDefault'])))
        
        if version == 'index' or addonType == 'index':
            result = result[:1000]
        
        return result
        

    TEMPLATE = open('public/index.html', "r", encoding="utf8").read()
    template = Template(TEMPLATE)

    ADDON_TYPES = ['mods', 'resourcePacks', 'modpacks', 'worlds']
    addonTypeHumanizer = {
        'bukkitPlugins': 'Bukkit Plugins',
        'mods': 'Mods',
        'resourcePacks': 'Resource Packs',
        'worlds': 'Worlds',
        'modpacks': 'Modpacks',
        'customizations': 'Customizations',
        'addons': 'Addons',
        'index': 'Addons'
    }
    VERSIONS = ['1.0.0', '1.0.1', '1.1', '1.2.5', '1.3.2', '1.4.7', '1.5.2', '1.6.4', '1.7.10', '1.8.9', '1.9.4', '1.10.2', '1.11.2', '1.12.2', '1.13.2', '1.14.4', '1.15.2', '1.16.5', '1.17.1', '1.18.2', '1.19.2', '1.19.3']
    MAIN_VERSIONS = ['1.2.5', '1.4.7', '1.6.4', '1.7.10', '1.8.9', '1.12.2', '1.16.5', '1.18.2']

    for addonType in ADDON_TYPES + ["index"]:
        for version in VERSIONS + ["index"]:
            print("Generating", addonType, "/", version)
            
            isIndex = addonType == "index" and version == "index"
            
            addons = list(createTemplateEntries(index, addonType, version))
            
            if not isIndex:
                os.makedirs("public/" + addonType, exist_ok=True)
            
            out = "public/" + addonType + "/" + version + ".html" if not isIndex else "public/index.html"
            
            with open(out, "w", encoding="utf8") as fp:
                fp.write(template.render(
                    addons=addons,
                    rootPath="../" if not isIndex else "./",
                    versions=VERSIONS,
                    mainVersions=MAIN_VERSIONS,
                    altVersions=[x for x in VERSIONS if x not in MAIN_VERSIONS],
                    selectedAddonType=addonType,
                    addonTypes=ADDON_TYPES,
                    addonTypeHumanizer=addonTypeHumanizer,
                    addonCount=len(addons),
                    updateTime=humanizeIsoTimestamp(datetime.datetime.utcfromtimestamp(index['lastModified']).isoformat()),
                    selectedVersion=version,
                    isIndex = version == 'index' or addonType == 'index',
                    )
                )
