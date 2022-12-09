import os
import datetime
import requests

print("SECRET_TEST inside hello.py is...")
if "SECRET_TEST" in os.environ:
    print(os.environ["SECRET_TEST"])
else:
    print("nuffin.")

print("SECRET_TEST backwards inside hello.py is...")
if "SECRET_TEST" in os.environ:
    print(os.environ["SECRET_TEST"][::-1])
else:
    print("nuffin.")

memory = []

if not os.path.isdir("data"):
    os.mkdir("data")

if os.path.exists("data/memory.txt"):
    memory = [x.strip() for x in list(open("data/memory.txt", "r", encoding="utf8"))]

print("memory:", memory)

memory.append("It is now " + datetime.datetime.now(datetime.timezone.utc).isoformat())

def getCurseHeaders(token):
    return {'Content-Type': 'application/json', 'Accept': 'application/json', 'x-api-key': token}

resp = requests.get("https://api.curseforge.com/v1/mods/search?gameId=432&sortField=3&sortOrder=desc&pageSize=1", headers = getCurseHeaders(os.environ["CURSEFORGE_TOKEN"]))
print("response:", resp.json())

with open("public/index.html", "w", encoding="utf8") as fp:
    fp.write("<p>hi.</p>")
    
    for entry in memory:
        fp.write("<p>" + entry + "</p>")

with open("public/text.txt", "w", encoding="utf8") as fp:
    fp.write("this is text")

with open("data/memory.txt", "w", encoding="utf8") as fp:
    fp.write("\n".join(memory))
