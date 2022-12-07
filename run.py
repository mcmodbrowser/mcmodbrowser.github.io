import importlib
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: {} TASK".format(sys.argv[0]))
    
    mod = importlib.import_module("mcmodbrowser.task.{}".format(sys.argv[1]))
    mod.run()
