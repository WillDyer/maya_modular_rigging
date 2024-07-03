import maya.cmds as cmds

class create_hands():
    def __init__(self) -> None:
        pass
    
    def module_hand(self):
        system = ["proximal","intermediate","distal","distalend"]
        system_pos = {"proximal": [2,0,0], "intermediate": [4,0,0], "distal": [6,0,0], "distalend": [8,0,0]}
        system_rot = {"proximal": [0,0,0], "intermediate": [0,0,0], "distal": [0,0,0], "distalend": [0,0,0]}
        side = "_l"
        #phalanx

        