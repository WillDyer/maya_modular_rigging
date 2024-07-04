import maya.cmds as cmds


def get_joint_list(orientation,skeleton_roots,system):
    jnts_list = []

    for top_skeleton_joint in skeleton_roots:
        # NEEDING TO IMPLEMENT NAME CHECK FOR UNIQUE NAMING THEN ADDING A VERSION UP SCHEME DO THIS ASAP
        jnt_list = joint(orientation, top_skeleton_joint, system)
        jnts_list.append(jnt_list)

    return jnts_list

def joint(orientation,top_skeleton_joint, system):
    #orientation = "xyz"
    prefix = "jnt"
    joint_tag = f"{prefix}_{system}_"
    jnt_names = []
    list_ctrls = []
    list = []

    list = cmds.listRelatives(top_skeleton_joint, ad=True, type="transform")
    if top_skeleton_joint == "root":
        list.append(top_skeleton_joint)
    elif "proximal" in top_skeleton_joint:
        list.append(top_skeleton_joint)
    list.reverse()

    side = cmds.getAttr(f"{top_skeleton_joint}.module_side",asString=1)
    if side == "None":
        side = ""
    
    for x in list:
        if "cluster" in x:
            pass
        else:
            list_ctrls.append(x)

    cmds.select(clear=1)
    for locator in list_ctrls:
        loc = cmds.xform(locator, r=True, ws=True, q=True, t=True) # Gather locator location
        jnt_name = cmds.joint(n=f"{joint_tag}{locator}", p=loc) # create joint based off the location
        jnt_names.append(jnt_name)

    # Orient joint
    cmds.joint(f"{joint_tag}{list_ctrls[0]}", edit=True, zso=1, oj=orientation, sao="xup", ch=True)
    # Orient end joint to world
    cmds.joint(f"{joint_tag}{list_ctrls[-1]}", e=True, oj="none" ,ch=True, zso=True)
    return jnt_names
