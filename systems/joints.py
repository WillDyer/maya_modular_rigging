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
        loc = cmds.xform(locator, r=True, ws=True, q=True, t=True)  # Gather locator location
        jnt_name = cmds.joint(n=f"{joint_tag}{locator}", p=loc)  # create joint based off the location
        jnt_names.append(jnt_name)
    mirror_attribute = cmds.getAttr(f"{top_skeleton_joint}.mirror_orientation", asString=1)

    if mirror_attribute == "Yes": sao_axis = "xdown"
    else: sao_axis = "xup"
    # Orient joint
    cmds.joint(f"{joint_tag}{list_ctrls[0]}", edit=True, zso=1, oj=orientation, sao=sao_axis, ch=True)
    # Orient end joint to world
    cmds.joint(f"{joint_tag}{list_ctrls[-1]}", e=True, oj="none",ch=True, zso=True)
    return jnt_names


def insert_joints_between(joint1, joint2, num_joints):
    if num_joints <= 0:
        print("Number of joints to insert must be greater than 0.")
        return
    tween_joint_list = []

    pos1 = cmds.xform(joint1, q=True, ws=True, t=True)
    pos2 = cmds.xform(joint2, q=True, ws=True, t=True)

    step = [(pos2[0] - pos1[0]) / (num_joints + 1),
            (pos2[1] - pos1[1]) / (num_joints + 1),
            (pos2[2] - pos1[2]) / (num_joints + 1)]

    previous_joint = joint1
    for i in range(1, num_joints + 1):
        new_position = [pos1[0] + step[0] * i,
                        pos1[1] + step[1] * i,
                        pos1[2] + step[2] * i]
        new_joint = cmds.joint(p=new_position,n="joint_#")
        if i == 1:
            first_joint = new_joint
        tween_joint_list.append(new_joint)
        previous_joint = new_joint

    cmds.parent(joint2, previous_joint)
    cmds.parent(first_joint, joint1)

    cmds.joint(first_joint, edit=True, zso=1, oj="xyz", sao="xup", ch=True)

    return tween_joint_list
