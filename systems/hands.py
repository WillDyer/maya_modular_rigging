import maya.cmds as cmds
import sys, os
import importlib
from systems import create_guides
importlib.reload(create_guides)


class create_hands():
    def __init__(self, guide_list,systems_to_be_made, created_guides):
        self.systems_to_be_made = systems_to_be_made
        self.created_guides = created_guides
        self.module_hand(guide_list)
        self.make_guides()
    
    def module_hand(self, guide_list):
        self.module = "hand"
        self.to_connect_to = [guide_list]
        print(f"to_connect_to: {self.to_connect_to}")
        self.offset = [0,0,0]
        #phalanx

    def make_guides(self):
        self.hand_dict = {}
        hand_master_guides = []
        module = importlib.import_module(f"systems.modules.{self.module}")
        importlib.reload(module)
        cmds.select(clear=1)
        amount = 5

        for x in range(amount):
            guides = create_guides.Guides(self.module,self.offset,module.side,self.to_connect_to)
            guide = guides.collect_guides()
            if guide:
                master_guide = guide["master_guide"]
                guide_connector_list = guide["connector_list"]
                system_to_connect = guide["system_to_connect"]
                guide_list = guide["ui_guide_list"]

                temp_dict = {
                    "module": self.module,
                    "master_guide": master_guide,
                    "guide_list": guide_list,
                    "joints": [],
                    "side": module.side,
                    "connectors": guide_connector_list,
                    "system_to_connect": system_to_connect,
                    "space_swap": [],
                    "ik_ctrl_list": [],
                    "fk_ctrl_list": [],
                    "ik_joint_list": [],
                    "fk_joint_list": []
                }
                self.systems_to_be_made[master_guide] = temp_dict
                self.created_guides.append(temp_dict["master_guide"])
                hand_master_guides.append(temp_dict["master_guide"])

        hand_grp = cmds.group(n=f"grp_{self.module}{module.side}_#",em=1,w=1)
        cmds.parent(hand_master_guides, hand_grp)
        cmds.matchTransform(hand_grp,self.to_connect_to)
        return self.systems_to_be_made
    
    def get_dict(self):
        return self.systems_to_be_made

    def get_created_guides(self):
        return self.created_guides