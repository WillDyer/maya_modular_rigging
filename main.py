import importlib
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ui

importlib.reload(ui) # remove after debug

def run_ui():
    ui.main()
    print("main run")
    
# run_ui()