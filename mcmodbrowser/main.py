import importlib

def runTask(name, args=[]):
    print("\n>> Running task:", name, args)
    mod = importlib.import_module("mcmodbrowser.task.{}".format(name))
    mod.run(args)
