import maya.cmds as cmds
from systems.utils import OPM

class SpaceSwapping():
    def __init__(self, key):
        self.system_to_be_made = key
        self.locator_list = self.system_to_be_made["space_swap"]
        self.guide_list = self.system_to_be_made["guide_list"]
        
        self.space_swap_locators = self.create_locators()
        if self.system_to_be_made["ik_ctrl_list"]:
            self.cog_ctrl = next(item for item in cmds.ls("ctrl_*") if "COG" in item)
            self.root_ctrl = next(item for item in cmds.ls("ctrl_*") if "root" in item)
            self.ik_ctrls = self.system_to_be_made["ik_ctrl_list"]
            self.handle_ctrl = [x for x in self.ik_ctrls if cmds.attributeQuery("handle", node=x, exists=True) and cmds.getAttr(f"{x}.handle", asString=1) == "True"]
            self.parent_to_location()
            self.blend_matrix()
            for x in self.ik_ctrls:
                try: OPM.offsetParentMatrix(x) 
                except: pass

    def create_locators(self):
        created_locator_list = [cmds.spaceLocator(n=f"loc_space_{x}")[0] for x in self.guide_list for item in self.locator_list if item in x]
        tmp_list = [cmds.spaceLocator(n=f"loc_space_{item}_#")[0] for x in self.locator_list for item in ["root","COG"] if item in x]
        created_locator_list.extend(tmp_list)
        if "Custom" in self.locator_list:
            loc = cmds.spaceLocator(n=f"loc_space_custom_#")[0]
            created_locator_list.append(loc)
            self.custom_loc = loc
        return created_locator_list

    def parent_to_location(self):
        def move_and_parent(locator, target):
            cmds.matchTransform(locator, self.handle_ctrl[0])
            cmds.parent(locator, target)

        for locator in self.space_swap_locators:
            if any(item in locator for item in self.locator_list):
                if self.cog_ctrl[5:] in locator:
                    move_and_parent(locator, self.cog_ctrl)
                if self.root_ctrl[5:] in locator:
                    move_and_parent(locator, self.root_ctrl)
                    
        check_against_ik_ctrls = [f"loc_space_{x}" for x in self.guide_list if any(x in item for item in self.ik_ctrls)]
        
        for locator in self.space_swap_locators:
            if locator in check_against_ik_ctrls:
                move_and_parent(locator, f"ctrl_ik{locator[9:]}")
        
        if self.custom_loc:
            move_and_parent(self.custom_loc, self.cog_ctrl)
    
    def get_loc(self,selection):
        pos = cmds.xform(selection, q=1, t=True, ws=True)
        return pos

    def blend_matrix(self):
        matrix_node = cmds.createNode("blendMatrix",n=f"matrix_{self.system_to_be_made['master_guide']}")
        joined_list = ':'.join(self.locator_list)
        cmds.group(self.handle_ctrl[0],n=f"grp_offset_{self.handle_ctrl[0]}",p="grp_offset_ik_hdls")
        cmds.addAttr(self.ik_ctrls[-1], ln="Space_Swap",at="enum",en=joined_list,k=1)
        cmds.addAttr(self.ik_ctrls[:-1],ln="Space_Swap", proxy=f"{self.ik_ctrls[-1]}.Space_Swap")
        for x in range(len(self.space_swap_locators)):
            condition_node = cmds.shadingNode("condition",n=f"condition_{self.space_swap_locators[x]}",au=1)
            for y in ["colorIfFalseR","colorIfFalseG","colorIfFalseG","colorIfTrueR","colorIfTrueG","colorIfTrueB"]: cmds.setAttr(f"{condition_node}.{y}",0)
            cmds.setAttr(f"{condition_node}.colorIfTrueR",1)
            cmds.setAttr(f"{condition_node}.secondTerm",x)
            cmds.connectAttr(f"{self.handle_ctrl[0]}.Space_Swap",f"{condition_node}.firstTerm")
            cmds.connectAttr(f"{self.space_swap_locators[x]}.worldMatrix[0]", f"{matrix_node}.target[{x}].targetMatrix",f=1)
            cmds.connectAttr(f"{condition_node}.outColorR",f"{matrix_node}.target[{x}].weight",f=1)
        cmds.connectAttr(f"{self.handle_ctrl[0]}.worldMatrix[0]",f"{matrix_node}.inputMatrix")
        cmds.disconnectAttr(f"{self.handle_ctrl[0]}.worldMatrix[0]",f"{matrix_node}.inputMatrix")
        cmds.connectAttr(f"{matrix_node}.outputMatrix",f"{self.handle_ctrl[0]}.offsetParentMatrix")
