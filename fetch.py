import os
import sys
from mcmodbrowser.main import runTask

limitRequests = "--limit-requests" in sys.argv[1:]

extraArgs = ["--request-limit", 1] if limitRequests else []

if not os.path.exists("data/index.json"):
    runTask("curse_fetch_all", [] + extraArgs)

runTask("curse_fetch_new", [] + extraArgs)
runTask("curse_fetch_file_dates", [] + extraArgs)
