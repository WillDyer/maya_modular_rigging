from importlib import reload
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(f"Adding to MAYA_SCRIPT_PATH ENV {os.path.dirname(os.path.abspath(__file__))}")

from . import interface
reload(interface)

interface.main()
print("init ran")
