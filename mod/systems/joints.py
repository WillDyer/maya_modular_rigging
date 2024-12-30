import maya.cmds as cmds


def get_joint_list(orientation,skeleton_roots,system):
    jnts_list = []

    for top_skeleton_joint in skeleton_roots:
        # NEEDING TO IMPLEMENT NAME CHECK FOR UNIQUE NAMING THEN ADDING A VERSION UP SCHEME DO THIS ASAP
        jnt_list = joint(orientation, top_skeleton_joint, system)
        jnts_list.append(jnt_list)

    return jnts_list


def joint(orientation,top_skeleton_joint, system):
    # orientation = "xyz"
    prefix = "jnt"
    joint_tag = f"{prefix}_{system}_"
    jnt_names = []
    list_ctrls = []
    list = []

    list = cmds.listRelatives(top_skeleton_joint, ad=True, type="transform")
    if "root" in top_skeleton_joint:
        list.append(top_skeleton_joint)
    elif "proximal" in top_skeleton_joint:
        list.append(top_skeleton_joint)
    list.reverse()

    for x in list:
        if "cluster" in x or "data_" in x:
            pass
        else:
            list_ctrls.append(x)

    cmds.select(clear=1)
    for locator in list_ctrls:
        loc = cmds.xform(locator, q=True, ws=True, t=True)  # Gather worldspace location
        rot = cmds.xform(locator, q=True, ws=True, ro=True) # gather worldspace rotation
        jnt_name = cmds.joint(n=f"{joint_tag}{locator}", p=loc)  # create joint based off the location
        cmds.xform(jnt_name, ws=True, ro=rot)
        # cmds.makeIdentity(jnt_name, apply=True, t=False, r=True, s=False)
        jnt_names.append(jnt_name)

    mirror_attribute = cmds.getAttr(f"{top_skeleton_joint}.mirror_orientation", asString=1)
    if mirror_attribute == "Yes": sao_axis = f"{orientation[0]}down"
    else: sao_axis = f"{orientation[0]}up"
    
    ### Old orientation code - keeping in case needed ###
    # Orient joint
    # cmds.joint(f"{joint_tag}{list_ctrls[0]}", edit=True, zso=1, oj=orientation, sao=sao_axis, ch=True)
    # Orient end joint to world
    # cmds.joint(f"{joint_tag}{list_ctrls[-1]}", e=True, oj="none",ch=True, zso=True)

    cmds.setAttr(f"{joint_tag}{list_ctrls[0]}.overrideEnabled",1)
    return jnt_names
