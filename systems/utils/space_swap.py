import maya.cmds as cmds

class SpaceSwapping():
    def __init__(self, key):
        self.system_to_be_made = key
        self.locator_list = key["space_swap"]
        self.create_locators()

    def create_locators(self):
        created_locator_list = [cmds.spaceLocator(n=f"loc_space_{x}")[0] for x in self.locator_list]
        print(created_locator_list)

