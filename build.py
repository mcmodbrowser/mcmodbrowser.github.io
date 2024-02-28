import sys
import glob
import os
from mcmodbrowser.main import runTask

def listTasks():
    tasks = []
    for file in glob.glob("mcmodbrowser/task/*.py"):
        base = os.path.basename(file).split(".")[0]
        if base != "__init__":
            tasks.append(base)
    return sorted(tasks)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('''Usage: {} TASK [ARG...]

Available tasks:\n{}'''.format(sys.argv[0], "\n".join(["    " + x for x in listTasks()])))
    
    runTask(sys.argv[1], sys.argv[2:])
