import maya.cmds as cmds
from mod.rig.utils import OPM


attrs = {
    'visibility_divider': ['VISIBILITY','------------',True,False,'not needed'],
    'vis_geometry': ['Geometry','Shown:Hidden',False,True,'geo.visibility'],
    'lock_divider': ['LOCK','------------',True,False,'not needed'],
    'export_geometry': ['Export Geometry','Unlocked:Wireframe:Locked',False,False,'not needed'],
    'debug_divider': ['DEBUG','------------',True,False,'not needed'],
    'rig_system': ['Rig System','Shown:Hidden',False,True,'grp_rig_jnts.visibility'],
    'skn_system': ['Skin System','Shown:Hidden',False,True,'grp_skn_jnts.visibility'],
    'ik_hndle_system': ['IK Handles','Shown:Hidden',False,True,'grp_ik_handles.visibility']
}


def sys_attr():
    for item in attrs.keys():
        cmds.addAttr("ctrl_root",sn=item,nn=attrs[item][0],k=True,at="enum",en=attrs[item][1])
        cmds.setAttr(f"ctrl_root.{item}",lock=attrs[item][2])
        if attrs[item][3] is True:
            cmds.createNode('reverse', n=f'reverse_{item}')
            cmds.connectAttr(f"ctrl_root.{item}",f"reverse_{item}.inputX")
            cmds.connectAttr(f"reverse_{item}.outputX",attrs[item][4])
    # for xyz in ["X","Y","Z"]:
    #     cmds.setAttr(f"ctrl_root.scale{xyz}",k=False,lock=True)

    cmds.setAttr("ctrl_root.skn_system", 1)
    cmds.setAttr("ctrl_root.ik_hndle_system", 1)


def grpSetup(rig_name):
    selection = cmds.ls(sl=True, typ='joint')

    cvs_front = [[7.8361162489122504, 4.798237340988468e-16, 56.627390816372774], [-1.2643170607829326e-15, 6.785732323110914e-16, 56.16118797606565], [-7.8361162489122425, 4.798237340988471e-16, 56.627390816372774], [-11.08194187554388, 1.9663354616187858e-31, 58.24909276049249], [-7.836116248912245, -4.79823734098847e-16, 67.49027876158601], [-3.3392053635905195e-15, -6.785732323110915e-16, 76.70217514296529], [7.836116248912238, -4.798237340988472e-16, 67.49027876158603], [11.08194187554388, -3.6446300679047923e-31, 58.249092760492495]]
    cvs_right = [[-56.627390816372774, 4.440892098500626e-16, 7.836116248912264], [-56.16118797606565, 6.661338147750939e-16, 1.1205971735482982e-14], [-56.627390816372774, 4.440892098500626e-16, -7.83611624891223], [-58.24909276049249, 1.9721522630525295e-31, -11.081941875543867], [-67.49027876158601, -4.440892098500626e-16, -7.83611624891223], [-76.70217514296529, -6.661338147750939e-16, 1.3692098812919765e-14], [-67.49027876158603, -4.440892098500626e-16, 7.836116248912253], [-58.249092760492495, -3.944304526105059e-31, 11.081941875543892]]
    cvs_back = [[-7.836116248912258, 4.440892098500626e-16, -56.627390816372774], [-5.613444848337229e-15, 6.661338147750939e-16, -56.16118797606565], [7.836116248912235, 4.440892098500626e-16, -56.627390816372774], [11.081941875543873, 1.9721522630525295e-31, -58.24909276049249], [7.836116248912237, -4.440892098500626e-16, -67.49027876158601], [-6.0541019640566935e-15, -6.661338147750939e-16, -76.70217514296529], [-7.836116248912246, -4.440892098500626e-16, -67.49027876158603], [-11.081941875543887, -3.944304526105059e-31, -58.249092760492495]]
    cvs_left = [[56.627390816372774, 4.440892098500626e-16, -7.836116248912264], [56.16118797606565, 6.661338147750939e-16, -1.1205971735482982e-14], [56.627390816372774, 4.440892098500626e-16, 7.83611624891223], [58.24909276049249, 1.9721522630525295e-31, 11.081941875543867], [67.49027876158601, -4.440892098500626e-16, 7.83611624891223], [76.70217514296529, -6.661338147750939e-16, -1.3692098812919765e-14], [67.49027876158603, -4.440892098500626e-16, -7.836116248912253], [58.249092760492495, -3.944304526105059e-31, -11.081941875543892]]
    cog_cvs = [[3.9180581244561252, 2.399118670494234e-16, 28.17862279228172], [-6.321585303914663e-16, 3.392866161555457e-16, 28.17860656315399], [-3.9180581244561212, 2.3991186704942355e-16, 28.17862279228172], [-5.54097093777194, 9.831677308093929e-32, 29.3225985797024], [-3.9180581244561226, -2.399118670494235e-16, 33.59997589662741], [-1.6696026817952597e-15, -3.3928661615554574e-16, 38.44910014660382], [3.918058124456119, -2.399118670494236e-16, 33.59997589662741], [5.54097093777194, -1.8223150339523961e-31, 29.322598579702404]]
    root_world_cvs = [[96.27788690389305, 4.798237340988468e-16, -96.27788690389288], [-1.067328100082453e-14, 6.785732323110914e-16, -93.55302031536176], [-96.27788690389283, 4.798237340988471e-16, -96.27788690389289], [-93.55302031536182, 1.9663354616187858e-31, -3.37190898278349e-14], [-96.27788690389283, -4.79823734098847e-16, 96.27788690389289], [-2.818935081283464e-14, -6.785732323110915e-16, 93.55302031536182], [96.27788690389282, -4.798237340988472e-16, 96.27788690389292], [93.55302031536182, -3.6446300679047923e-31, 4.36377446562675e-14]]
    
    root_world = cmds.circle(n="ctrl_root_world", nr=(0,1,0))[0]
    root_world_shape = cmds.listRelatives(root_world, shapes=True, fullPath=True)[0]
    root_world_shape_cvs = cmds.ls(f"{root_world_shape}.cv[*]", flatten=True)
    for i, cv in enumerate(root_world_cvs):
        cmds.xform(root_world_shape_cvs[i], translation=cv, os=True)
    cmds.setAttr(f"{root_world}.scale", lock=True, k=False)

    root = cmds.circle(n="ctrl_root",r=50,nr=(0, 1, 0))[0]
    for cv_set in [cvs_front, cvs_right, cvs_back, cvs_left]:
        new_shape = cmds.circle(n="ctrl_root")
        new_shape_node = cmds.listRelatives(new_shape, shapes=True, fullPath=True)[0]
        cvs_new = cmds.ls(f"{new_shape_node}.cv[*]", flatten=True)
        for i, cv in enumerate(cv_set):
            cmds.xform(cvs_new[i], translation=cv, os=True)
        cmds.parent(new_shape_node, root, shape=True,r=True)
        cmds.delete(new_shape)

    COG = cmds.circle(n="ctrl_COG",r=25,nr=(0, 1, 0))[0]
    new_shape = cmds.circle(n="ctrl_COGShape")
    new_shape_node = cmds.listRelatives(new_shape, shapes=True, fullPath=True)[0]
    cvs_new = cmds.ls(f"{new_shape_node}.cv[*]", flatten=True)
    for i, cv in enumerate(cog_cvs):
        cmds.xform(cvs_new[i], translation=cv, os=True)
    cmds.parent(new_shape_node, COG, shape=True, relative=True)
    cmds.delete(new_shape)
    cog_jnt = [item for item in cmds.ls("jnt_rig*") if "COG" in item]

    if cog_jnt:
        cmds.matchTransform("ctrl_COG", cog_jnt[0],pos=1)
        OPM.offsetParentMatrix(ctrl="ctrl_COG")

    # try:
    grpList = ['geo','grp_controls','grp_joints']
    jntList = ['grp_ik_handles','grp_rig_jnts','grp_skn_jnts']
    # ctrlList = ['grp_ctrls_head','grp_ctrls_spine','grp_ctrls_arms','grp_ctrls_legs']

    cmds.group(n=rig_name,w=True,em=True)

    cmds.group(n="grp_rig", p=rig_name,em=True)
    cmds.group(n='world_space',p=rig_name,em=True)

    for x in grpList:
        cmds.group(n=x,p="grp_rig",em=True)
    for x in jntList:
        cmds.group(n=x,p=grpList[2],em=True)

    cmds.group(n='grp_offset_ik_hdls',p='grp_controls',em=True)
    cmds.parent('ctrl_root_world','grp_controls')
    cmds.parent('ctrl_root','ctrl_root_world')

    cmds.parent('ctrl_COG','ctrl_root')

    cmds.group(n='modules',p='ctrl_COG',em=True)

    for type in ["render", "muscle", "bone"]:
        cmds.group(n=type, p="geo", em=True)

    sys_attr()


def heirachy_parenting(systems_dict):
    for key in systems_dict.values():
        master_guide = key["master_guide"]
        if "root" in master_guide: pass
        else:
            grp_fk_ctrl = f"grp_fk_ctrls_{master_guide}"
            grp_ik_ctrl = f"grp_ik_ctrls_{master_guide}"
            grp_fk_jnts = f"grp_fk_jnts_{master_guide}"
            grp_ik_jnts = f"grp_ik_jnts_{master_guide}"
            grp_tweaks_ctrl = f"grp_tweak_{master_guide}"
            grp_twisk_jnts = f"grp_twist_jnts_{master_guide}"

            if cmds.getAttr(f"{master_guide}.base_module", asString=1) == "hand":
                master_guide = f"{key['side']}{[key['hand_grp_num']][0]}_{cmds.getAttr(f'{master_guide}.base_module', asString=1)}"

            if "master" in master_guide:
                master_guide = master_guide.replace("master_","")
            
            if not cmds.objExists(master_guide):
                cmds.group(n=master_guide,p="modules",em=1)
            try:
                cmds.parent(cmds.listRelatives(grp_fk_jnts,c=1), master_guide)
                cmds.delete(grp_fk_jnts)
            except ValueError: pass
            try:
                cmds.parent(cmds.listRelatives(grp_ik_jnts,c=1), master_guide)
                cmds.delete(grp_ik_jnts)
            except ValueError: pass
            try:
                cmds.parent(cmds.listRelatives(grp_twisk_jnts,c=1), master_guide)
                cmds.delete(grp_twisk_jnts)
            except ValueError: pass
            try: cmds.parent(grp_fk_ctrl, master_guide)
            except ValueError: pass
            try: cmds.parent(grp_ik_ctrl, master_guide)
            except ValueError: pass
            try: cmds.parent(grp_tweaks_ctrl, master_guide)
            except ValueError: pass

    hdl_list = cmds.ls("hdl_ik_*")
    if hdl_list:
        for hdl in hdl_list:
            parent = cmds.listRelatives(hdl, parent=True)
            if not parent: cmds.parent(hdl,"grp_ik_handles")

    tmp_world_space = cmds.ls("tmp_world_space")
    if tmp_world_space:
        children = cmds.listRelatives(tmp_world_space, c=1)
        cmds.parent(children, "world_space")
        cmds.delete("tmp_world_space")

    ctrl_ribbon_list = cmds.ls("grp_ctrl_ribbon_*")
    if ctrl_ribbon_list:
        try: cmds.parent(ctrl_ribbon_list, "modules")
        except RuntimeError: pass
    parent_ribbon_list = cmds.ls("grp_parent_ribbon_*")
    if parent_ribbon_list:
        cmds.group(n="grp_ribbons",p="grp_rig",em=1)
        try: cmds.parent(parent_ribbon_list, "grp_ribbons")
        except RuntimeError: pass

    cog_jnt = [item for item in cmds.ls("jnt_rig*") if "cog" in item]
    if cog_jnt in cmds.ls("jnt_rig_COG"):
        rig_root_jnt = next(item for item in cmds.ls("jnt_rig_*") if "root" in item)
        skn_root_jnt = next(item for item in cmds.ls("jnt_skn_*") if "root" in item)

        cmds.parent(rig_root_jnt, "grp_rig_jnts")
        cmds.parent(skn_root_jnt, "grp_skn_jnts")
    else:
        all_joints = cmds.ls(type='joint')
        world_parented_joints = [joint for joint in all_joints if not cmds.listRelatives(joint, parent=True)]
        for joint in world_parented_joints:
            if "rig" in joint:
                cmds.parent(joint, "grp_rig_jnts")
            elif "skn" in joint:
                cmds.parent(joint, "grp_skn_jnts")
            else: pass

    root_jnt = [item for item in cmds.ls("jnt_rig*") if "root" in item]
    cog_jnt = [item for item in cmds.ls("jnt_rig_*") if "COG" in item]
    if root_jnt and cog_jnt:
        cmds.parentConstraint("ctrl_root",root_jnt,mo=1)
        cmds.parentConstraint("ctrl_COG",cog_jnt,mo=1)
    else:
        cmds.warning("system_group: No cog or root joint exists not connecting root/cog ctrl to joint.")
