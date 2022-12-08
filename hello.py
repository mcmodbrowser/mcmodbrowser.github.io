import os
import datetime


print("TEST_ENV inside hello.py is...")
if "TEST_ENV" in os.environ:
    print(os.environ["TEST_ENV"])
else:
    print("nuffin.")

memory = []

if not os.path.isdir("data"):
    os.mkdir("data")

if os.path.exists("data/memory.txt"):
    memory = [x.strip() for x in list(open("data/memory.txt", "r", encoding="utf8"))]

print("memory:", memory)

memory.append("It is now " + datetime.datetime.now(datetime.timezone.utc).isoformat())

with open("public/index.html", "w", encoding="utf8") as fp:
    fp.write("<p>hi.</p>")
    
    for entry in memory:
        fp.write("<p>" + entry + "</p>")

with open("public/text.txt", "w", encoding="utf8") as fp:
    fp.write("this is text")

with open("data/memory.txt", "w", encoding="utf8") as fp:
    fp.write("\n".join(memory))
