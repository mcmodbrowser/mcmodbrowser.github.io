import glob
import os
import sys
import shutil
import json
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
            'lastModifiedDefault': '0000-00-00'
        })
    
    return result
    

TEMPLATE = open('public/index.html', "r", encoding="utf8").read()
template = Template(TEMPLATE)

#for addonType in ['bukkitPlugins', 'mods', 'resourcePacks', 'worlds', 'modpacks', 'customizations', 'addons']:
for addonType in ['mods']:
    for version in ['1.7.10']:
        addons = createTemplateEntries(index['data'][addonType], version)
        
        os.makedirs("public/" + addonType, exist_ok=True)
        
        with open("public/" + addonType + "/" + version + ".html", "w", encoding="utf8") as fp:
            fp.write(template.render(addons=addons, rootPath="../"))
