import importlib
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(f"Adding to MAYA_SCRIPT_PATH ENV {os.path.dirname(os.path.abspath(__file__))}")

import interface
importlib.reload(interface)


def run_ui():
    interface.main()
    print("main run")

# run_ui()
