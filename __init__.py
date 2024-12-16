from importlib import reload
import sys
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path)
print(f"Adding to MAYA_script_PATH ENV {dir_path}")

import mod
reload(mod)
