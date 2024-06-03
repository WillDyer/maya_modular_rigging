import maya.cmds as cmds

groups = {
    "ik_systems": ["ik_joints","ik_controls","ik_misc"],
    "fk_systems": ["fk_joints","fk_controls","fk_misc"],
    "rig_systems": ["rig_joints","rig_controls","rig_misc"],
    "skn_systems": ["skn_joints","skn_controls","skn_misc"]
}

def setup(group_prefix, module_name):
    cmds.group(n=f"{group_prefix}_{module_name}",w=True,em=True)
    cmds.group(n=f"{group_prefix}_locators_{module_name}", p=f"{group_prefix}_{module_name}",em=True)

    for item in groups:
        cmds.group(n=f"{group_prefix}_{item}_{module_name}", p=f"{group_prefix}_{module_name}", em=True,r=True)
        for sub_item in groups[item]:
            cmds.group(n=f"{group_prefix}_{sub_item}_{module_name}", p=f"{group_prefix}_{item}_{module_name}", em=True,r=True)
    
    cmds.select(f"{group_prefix}_{module_name}")
