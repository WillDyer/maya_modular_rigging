import maya.cmds as cmds
from systems.utils import OPM


attrs = {
    'visibility_divider': ['VISIBILITY','------------',True,False,'not needed'],
    'vis_geometry': ['Geometry','Shown:Hidden',False,True,'geo.visibility'],
    'lock_divider': ['LOCK','------------',True,False,'not needed'],
    'export_geometry': ['Export Geometry','Unlocked:Locked:Wireframe',False,False,'not needed'],
    'debug_divider': ['DEBUG','------------',True,False,'not needed'],
    'rig_system': ['Rig System','Shown:Hidden',False,True,'grp_rig_jnts.visibility'],
    'skn_system': ['Skin System','Shown:Hidden',False,True,'grp_skn_jnts.visibility'],
    'ik_hndle_system': ['IK Handles','Shown:Hidden',False,True,'grp_ik_handles.visibility']
}


def sys_attr():
    for item in attrs.keys():
        # print(attrs[item][0])
        cmds.addAttr("ctrl_root",sn=item,nn=attrs[item][0],k=True,at="enum",en=attrs[item][1])
        cmds.setAttr(f"ctrl_root.{item}",lock=attrs[item][2])
        if attrs[item][3] is True:
            cmds.createNode('reverse', n=f'reverse_{item}')
            cmds.connectAttr(f"ctrl_root.{item}",f"reverse_{item}.inputX")
            cmds.connectAttr(f"reverse_{item}.outputX",attrs[item][4])
    for xyz in ["X","Y","Z"]:
        cmds.setAttr(f"ctrl_root.scale{xyz}",k=False,lock=True)


grp_controls = ['ctrl_root','ctrl_COG','ctrl_root_world']


def grpSetup(rig_name):
    selection = cmds.ls(sl=True, typ='joint')
    ABC_FILE = "./imports/curve_import.abc"
    try:
        cmds.file(ABC_FILE, i=True)
    except RuntimeError:
        print("INFO: Couldnt load file using basic shapes instead")
        cmds.circle(n="ctrl_root",r=50,nr=(0, 1, 0))
        cmds.circle(n="ctrl_COG",r=25,nr=(0, 1, 0))
    cog_jnt = [item for item in cmds.ls("jnt_rig*") if "COG" in item]
    cmds.matchTransform("ctrl_COG", cog_jnt[0],pos=1)
    OPM.offsetParentMatrix(ctrl="ctrl_COG")

    # try:
    grpList = ['geo','grp_controls','grp_joints']
    jntList = ['grp_ik_handles','grp_rig_jnts','grp_skn_jnts']
    # ctrlList = ['grp_ctrls_head','grp_ctrls_spine','grp_ctrls_arms','grp_ctrls_legs']

    cmds.group(n=rig_name,w=True,em=True)

    cmds.group(n="grp_rig", p=rig_name,em=True)
    cmds.group(n='DO_NOT_TOUCH',p=rig_name,em=True)

    for x in grpList:
        cmds.group(n=x,p="grp_rig",em=True)
    for x in jntList:
        cmds.group(n=x,p=grpList[2],em=True)

    cmds.group(n='grp_root',p='grp_controls',em=True)
    cmds.group(n='grp_offset_ik_hdls',p='grp_controls',em=True)
    cmds.parent('ctrl_root','grp_root')
    cmds.group(n='grp_COG',p='ctrl_root',em=True)
    if "jnt_rig_COG" in cmds.ls("jnt_rig_COG"):
        cmds.matchTransform('grp_COG','jnt_rig_COG',pos=True,rot=True)

    cmds.parent('ctrl_COG','grp_COG')

    cmds.group(n='modules',p='ctrl_COG',em=True)

    for type in ["render", "muscle", "bone"]:
        cmds.group(n=type, p="geo", em=True)

    sys_attr()


def heirachy_parenting(systems_dict):
    master_guide_list = []
    for key in systems_dict.values(): master_guide_list.append(key["master_guide"])

    print(f"master_guide_list: {master_guide_list}")

    for master_guide in master_guide_list:
        if "root" in master_guide: pass
        else:
            grp_fk_ctrl = f"grp_fk_ctrls_{master_guide}"
            grp_ik_ctrl = f"grp_ik_ctrls_{master_guide}"
            grp_fk_jnts = f"grp_fk_jnts_{master_guide}"
            grp_ik_jnts = f"grp_ik_jnts_{master_guide}"
            grp_tweaks_ctrl = f"grp_tweak_{master_guide}"

            if "master" in master_guide:
                master_guide = master_guide.replace("master_","")
            cmds.group(n=master_guide,p="modules",em=1)
            try:
                cmds.parent(cmds.listRelatives(grp_fk_jnts,c=1), master_guide)
                cmds.delete(grp_fk_jnts)
            except ValueError: pass
            try:
                cmds.parent(cmds.listRelatives(grp_ik_jnts,c=1), master_guide)
                cmds.delete(grp_ik_jnts)
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

    ctrl_ribbon_list = cmds.ls("grp_ctrl_ribbon_*")
    if ctrl_ribbon_list:
        try: cmds.parent(ctrl_ribbon_list, "modules")
        except RuntimeError: pass
    parent_ribbon_list = cmds.ls("grp_parent_ribbon_*")
    if parent_ribbon_list:
        cmds.group(n="grp_ribbons",p="grp_rig",em=1)
        try: cmds.parent(parent_ribbon_list, "grp_ribbons")
        except RuntimeError: pass

    rig_root_jnt = next(item for item in cmds.ls("jnt_rig_*") if "root" in item)
    skn_root_jnt = next(item for item in cmds.ls("jnt_skn_*") if "root" in item)
    cog_jnt = next(item for item in cmds.ls("jnt_rig_*") if "COG" in item)

    cmds.parent(rig_root_jnt, "grp_rig_jnts")
    cmds.parent(skn_root_jnt, "grp_skn_jnts")

    cmds.parentConstraint("ctrl_root",rig_root_jnt,mo=1)
    cmds.parentConstraint("ctrl_COG",cog_jnt,mo=1)
