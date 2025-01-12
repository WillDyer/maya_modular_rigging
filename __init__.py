from importlib import reload
import sys
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path)

import mod.interface as interface
reload(interface)
from mod.interface import start_interface
