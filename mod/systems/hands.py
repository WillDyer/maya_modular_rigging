import maya.cmds as cmds
import importlib

from mod.systems import create_guides
from mod.systems.utils import OPM, guide_data

importlib.reload(create_guides)
importlib.reload(guide_data)


class create_hands():
    def __init__(self, guide_list,systems_to_be_made, created_guides, finger_amount):
        self.systems_to_be_made = systems_to_be_made
        self.created_guides = created_guides
        self.finger_amount = finger_amount

        self.module_hand(guide_list)
        self.make_guides()
        self.space_out()

        cmds.parent(self.hand_master_guides, self.hand_grp)
        cmds.matchTransform(self.hand_grp,self.to_connect_to)
        OPM.offsetParentMatrix(self.hand_grp)
        cmds.connectAttr(f"{self.to_connect_to[0]}.worldMatrix", f"{self.hand_grp}.offsetParentMatrix")

    def module_hand(self, guide_list):
        self.module = "hand"
        self.to_connect_to = [guide_list]
        self.offset = [0,0,0]

    def make_guides(self):
        self.hand_dict = {}
        self.hand_master_guides = []
        module = importlib.import_module(f"mod.systems.modules.{self.module}")
        importlib.reload(module)
        cmds.select(clear=1)
        self.hand_grp = cmds.group(n=f"grp_{self.module}_{module.side}#",em=1,w=1)
        cmds.select(clear=1)

        for x in range(int(self.finger_amount)):
            use_existing_attr = [cmds.getAttr(f"{self.to_connect_to[0]}.master_guide",asString=1)]
            guides = create_guides.Guides(self.module,self.offset,module.side,self.to_connect_to,use_existing_attr)
            guide = guides.collect_guides()
            if guide:
                master_guide = guide["master_guide"]
                guide_connector_list = guide["connector_list"]
                system_to_connect = guide["system_to_connect"]
                guide_list = guide["ui_guide_list"]
                data_guide = guide["data_guide"]
                guide_number = guide["guide_number"]

                self.temp_dict = {
                    "module": self.module,
                    "master_guide": master_guide,
                    "guide_list": guide_list,
                    "guide_scale": module.guide_scale,
                    "joints": [],
                    "side": module.side,
                    "connectors": guide_connector_list,
                    "system_to_connect": system_to_connect,
                    "space_swap": [],
                    "ik_ctrl_list": [],
                    "fk_ctrl_list": [],
                    "ik_joint_list": [],
                    "fk_joint_list": [],
                    "guide_number": guide_number,
                    "hand_grp_num": self.hand_grp[-1],
                    "hidden_obj": self.hand_grp
                }
                self.systems_to_be_made[master_guide] = self.temp_dict
                self.created_guides.append(self.temp_dict["master_guide"])
                self.hand_master_guides.append(self.temp_dict["master_guide"])
                guide_data.setup(self.temp_dict, data_guide)

        #self.hand_grp = cmds.group(n=f"grp_{self.module}_{module.side}#",em=1,w=1)
        self.systems_to_be_made["name"] = f"{self.hand_grp[-2:]}_{self.module}"
        self.systems_to_be_made["master_guide"] = self.hand_grp
        self.systems_to_be_made["module"] = self.module
        self.systems_to_be_made["system_to_connect"] = ["tmp_value", self.to_connect_to[0]]
        return self.systems_to_be_made

    def space_out(self):
        num_curves = len(self.hand_master_guides)
        initial_positions = [cmds.xform(curve, query=True, worldSpace=True, translation=True) for curve in self.hand_master_guides]

        # Calculate the spacing between the curves
        spacing = 2
        total_width = (num_curves - 1) * spacing  # Adjust 1.0 to your desired spacing
        start_z = - (total_width / 2.0)

        # Distribute the curves along the X-axis
        for i, curve in enumerate(self.hand_master_guides):
            initial_x, initial_y, initial_z = initial_positions[i]
            new_z = start_z + i * spacing
            cmds.xform(curve, worldSpace=True, translation=[initial_x, initial_y, new_z])

    def get_dict(self):
        return self.systems_to_be_made

    def get_created_guides(self):
        return self.created_guides

    def get_hand_grp_to_delete(self):
        return self.hand_grp

    def return_data(self):
        return self.temp_dict
