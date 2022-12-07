import json
import sys
import os

def loadJson(path):
    with open(path, "r", encoding="utf8") as fp:
        return json.load(fp)

def writeJson(data, path):
    with open(path, "w", encoding="utf8") as fp:
        json.dump(data, fp)

def getCurseToken():
    if 'CURSEFORGE_TOKEN' not in os.environ:
        sys.exit("You must set the CURSEFORGE_TOKEN environmental variable to your CurseForge API key.")
    return os.environ['CURSEFORGE_TOKEN']

def humanizeIsoTimestamp(ts):
    return " ".join(ts.split("Z")[0].split(".")[0].split("T"))
