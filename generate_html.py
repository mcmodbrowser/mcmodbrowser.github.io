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

def createTemplateEntry(mod):
    if 'authors' not in mod:
        print("WTF")
        print(mod)
    return {
    'name': mod['name'],
    'url': mod['url'],
    'description': mod['desc'],
    'authors': ', '.join(mod['authors']),
    'downloads': mod['downloads'],
    'downloadsFormatted': mod['downloads'],
    'lastModifiedDefault': '0000-00-00'
    }
    

mods = [createTemplateEntry(index['data']['mods'][mod]['curse']) for mod in index['data']['mods']]

for file in glob.glob("public/**/*.html", recursive=True):
    TEMPLATE = open(file, "r", encoding="utf8").read()

    template = Template(TEMPLATE)

    with open(file, "w", encoding="utf8") as fp:
        fp.write(template.render(mods=mods))