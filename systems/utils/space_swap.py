import maya.cmds as cmds

class SpaceSwapping():
    def __init__(self, key):
        self.system_to_be_made = key
        self.locator_list = self.system_to_be_made["space_swap"]
        self.guide_list = self.system_to_be_made["guide_list"]
        
        self.space_swap_locators = self.create_locators()
        if self.system_to_be_made["ik_ctrl_list"]:
            print("ik list found")
            self.ik_ctrls = self.system_to_be_made["ik_ctrl_list"]
            self.parent_to_location()

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
        cog_ctrl = [item for item in cmds.ls("ctrl_*") if "COG" in item]
        root_ctrl = [item for item in cmds.ls("ctrl_*") if "root" in item]

        for locator in self.space_swap_locators:
            for item in self.locator_list:
                if item in locator:
                    if item in cog_ctrl[0]:
                        print(f"found {item} in {cog_ctrl[0]}")
                        cmds.parent(locator, cog_ctrl[0])
                    if item in root_ctrl[0]:
                        cmds.parent(locator, root_ctrl[0])
                        print(f"found {item} in {root_ctrl[0]}")
        check_against_ik_ctrls = [f"loc_space_{x}" for x in self.guide_list for item in self.ik_ctrls if x in item]

        for locator in self.space_swap_locators:
            for item in check_against_ik_ctrls:
                if item == locator:
                    #print(f"parenting {locator} to {f'ctrl_ik{item[7:]}'}") # debug
                    cmds.parent(locator, f"ctrl_ik{item[9:]}")

        if self.custom_loc:
            cmds.parent(self.custom_loc, cog_ctrl[0])