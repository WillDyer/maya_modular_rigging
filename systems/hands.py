import maya.cmds as cmds
import sys, os
import importlib
from systems import create_guides
importlib.reload(create_guides)


class create_hands():
    def __init__(self):
        self.module_hand()
        self.make_guides()
    
    def module_hand(self):
        self.module = "hand"
        self.offset = [0,0,0]
        #phalanx

    def make_guides(self):
        print(f"module: {self.module}")
        module = importlib.import_module(f"systems.modules.{self.module}")
        importlib.reload(module)
        cmds.select(clear=1)
        amount = 5

        for x in range(amount):
            guides = create_guides.Guides(self.module,self.offset,module.side)
            pass