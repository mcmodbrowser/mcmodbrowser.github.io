import glob
import os
import sys
import shutil
import json
import datetime
from jinja2 import Template

if False in [os.path.exists(x) for x in [".git", "generate_html.py", "public_template"]]:
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
    mapping = fileDatesMapping
    points = fileDatesMappingKeys
    
    if p < points[0]:
        return (mapping[points[0]] - mapping[points[1]]) * (mapping[points[0]] - p)
    elif p > points[-1]:
        return (mapping[points[-1]] - mapping[points[-2]]) * (p - mapping[points[-1]])
    else:
        prevp = (p // 1000) * 1000
        while prevp not in points:
            prevp -= 1000
        
        nextp = ((p // 1000) + 1) * 1000
        while nextp not in points:
            nextp += 1000
        
        return mapping[prevp] + (mapping[nextp] - mapping[prevp]) * ((p - prevp) / (mapping[nextp] - mapping[prevp]))
        
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
    'addons': 'Addons'
}
VERSIONS = ['1.0.0', '1.0.1', '1.1', '1.2.5', '1.3.2', '1.4.7', '1.5.2', '1.6.4', '1.7.10', '1.8.9', '1.9.4', '1.10.2', '1.11.2', '1.12.2', '1.13.2', '1.14.4', '1.15.2', '1.16.5', '1.17.1', '1.18.2']
MAIN_VERSIONS = ['1.2.5', '1.4.7', '1.6.4', '1.7.10', '1.8.9', '1.12.2', '1.16.5', '1.18.2']

for addonType in ADDON_TYPES:
    for version in VERSIONS:
        print("Generating", addonType, "/", version)
        addons = list(createTemplateEntries(index['data'].get(addonType) or [], version))
        
        os.makedirs("public/" + addonType, exist_ok=True)
        
        with open("public/" + addonType + "/" + version + ".html", "w", encoding="utf8") as fp:
            fp.write(template.render(
                addons=addons,
                rootPath="../",
                versions=VERSIONS,
                mainVersions=MAIN_VERSIONS,
                altVersions=[x for x in VERSIONS if x not in MAIN_VERSIONS],
                selectedAddonType=addonType,
                addonTypes=ADDON_TYPES,
                addonTypeHumanizer=addonTypeHumanizer,
                addonCount=len(addons),
                updateTime="????-??-??",
                selectedVersion=version)
            )
