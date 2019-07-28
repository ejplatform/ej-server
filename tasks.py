import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "etc"))

#
# Import tasks at the etc/tasklib site
#
from tasklib.tasks import *
