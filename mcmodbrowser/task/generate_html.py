import glob
import os
import sys
import shutil
import json
import datetime
from jinja2 import Template
import os
from mcmodbrowser.util import humanizeIsoTimestamp

def run():
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
    fileDates = loadJson("data/fileDates.json")

    fileDatesMapping = {}
    for id, date in fileDates['data'].items():
        fileDatesMapping[int(id)] = date
    fileDatesMappingKeys = sorted([int(x) for x in fileDatesMapping.keys()])

    def fileIdToApproximateEpoch(p):
        '''Linearly interpolate between known fileId -> date mappings.'''
        mapping = fileDatesMapping
        points = fileDatesMappingKeys
        
        x0, y0, x1, y1 = (None, None, None, None)
        
        if p < points[0]:
            x0 = points[0]
            y0 = mapping[points[0]]
            x1 = points[1]
            y1 = mapping[points[1]]
        elif p > points[-1]:
            x0 = points[-2]
            y0 = mapping[points[-2]]
            x1 = points[-1]
            y1 = mapping[points[-1]]
        else:
            prevp = (p // 1000) * 1000
            while prevp not in points:
                prevp -= 1000
            
            nextp = ((p // 1000) + 1) * 1000
            while nextp not in points:
                nextp += 1000
            
            x0 = prevp
            y0 = mapping[prevp]
            x1 = nextp
            y1 = mapping[nextp]
        
        a = (y1 - y0) / (x1 - x0)
        b = y0 - a * x0
        # a*x0+b=y0 => b=y0-a*x0
        
        return a * p + b
            
    def fileIdToApproximateDate(p):
        return datetime.datetime.utcfromtimestamp(fileIdToApproximateEpoch(p)).isoformat().split("T")[0]

    def createTemplateEntries(addons, version):
        result = []
        
        for slug in addons:
            addonMulti = addons[slug]
            
            addon = addonMulti['curse']
            
            if not version in addon['versions']:
                continue
            
            result.append({
                'name': addon['name'],
                'url': addon['url'],
                'description': addon['desc'],
                'authors': ', '.join(addon['authors']),
                'downloads': addon['downloads'],
                'downloadsFormatted': addon['downloads'],
                'lastModifiedDefault': fileIdToApproximateDate(max(x['fileId'] for x in addon['versions'][version].values()))
            })
        
        result = reversed(sorted(result, key=lambda addon: addon['lastModifiedDefault']))
        
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
        'index': 'Mod Browser'
    }
    VERSIONS = ['1.0.0', '1.0.1', '1.1', '1.2.5', '1.3.2', '1.4.7', '1.5.2', '1.6.4', '1.7.10', '1.8.9', '1.9.4', '1.10.2', '1.11.2', '1.12.2', '1.13.2', '1.14.4', '1.15.2', '1.16.5', '1.17.1', '1.18.2']
    MAIN_VERSIONS = ['1.2.5', '1.4.7', '1.6.4', '1.7.10', '1.8.9', '1.12.2', '1.16.5', '1.18.2']

    for addonType in ADDON_TYPES + ["index"]:
        for version in VERSIONS + ["index"]:
            print("Generating", addonType, "/", version)
            
            isIndex = addonType == "index" and version == "index"
            
            addons = list(createTemplateEntries(index['data'].get(addonType) or [], version)) if not isIndex else []
            
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
                    updateTime=humanizeIsoTimestamp(index['lastUpdated']),
                    selectedVersion=version,
                    isIndex = version == 'index' or addonType == 'index',
                    )
                )
