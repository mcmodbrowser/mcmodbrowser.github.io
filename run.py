import importlib
import sys
import glob
import os

def listTasks():
    tasks = []
    for file in glob.glob("mcmodbrowser/task/*.py"):
        base = os.path.basename(file).split(".")[0]
        if base != "__init__":
            tasks.append(base)
    return sorted(tasks)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('''Usage: {} TASK

Available tasks are: {}'''.format(sys.argv[0], listTasks()))
    
    mod = importlib.import_module("mcmodbrowser.task.{}".format(sys.argv[1]))
    mod.run()
