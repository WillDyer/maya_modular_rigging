import maya.cmds as cmds

class space_swapping():
    def __init__(self, key):
        self.system_to_be_made = key
        self.locator_list = key["space_swapping"]

    def create_locators(self):
        created_locator_list = [cmds.spaceLocator(n=f"loc_space_{x}") for x in self.locator_list]
