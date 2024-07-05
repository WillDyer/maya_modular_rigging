import maya.cmds as cmds
import importlib
from systems.utils import OPM


attrs = {
    #'controls_divider': ['CONTROLS','------------',True,False,'not needed'],
    #'face': ['Face','Shown:Hidden',False,True,'grp_ctrls_head.visibility'],
    #'body': ['Body','Shown:Hidden',False,True,'grp_ctrls_spine.visibility'],
    #'arms': ['Arms','Shown:Hidden',False,True,'grp_ctrls_arms.visibility'],
    #'legs': ['Legs','Shown:Hidden',False,True,'grp_ctrls_legs.visibility'],
    'visibility_divider': ['VISIBILITY','------------',True,False,'not needed'],
    'vis_geometry': ['Geometry','Shown:Hidden',False,True,'grp_mesh.visibility'],
    'blend_shapes': ['Blendshapes','Shown:Hidden',False,True,'grp_blendshapes.visibility'],
    'lock_divider': ['LOCK','------------',True,False,'not needed'],
    'export_geometry': ['Export Geometry','Unlocked:Locked:Wireframe',False,False,'not needed'],
    'debug_divider': ['DEBUG','------------',True,False,'not needed'],
    'rig_system': ['Rig System','Shown:Hidden',False,True,'grp_rig_jnts.visibility'],
    'skn_system': ['Skin System','Shown:Hidden',False,True,'grp_skn_jnts.visibility'],
    'fk_system': ['FK System','Shown:Hidden',False,True,'grp_fk_jnts.visibility'],
    'ik_system': ['IK System','Shown:Hidden',False,True,'grp_ik_jnts.visibility'],
    'ik_hndle_system': ['IK Handles','Shown:Hidden',False,True,'grp_ik_handles.visibility']
}

def sys_attr():
    for item in attrs.keys():
        #print(attrs[item][0])
        cmds.addAttr("ctrl_root",sn=item,nn=attrs[item][0],k=True,at="enum",en=attrs[item][1])
        cmds.setAttr(f"ctrl_root.{item}",lock=attrs[item][2])
        if attrs[item][3] == True:
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
    


    #try:
    grpList = ['grp_mesh','grp_controls','grp_joints','grp_locators','grp_blendshapes']
    jntList = ['grp_ik_handles','grp_ik_jnts','grp_fk_jnts','grp_rig_jnts','grp_skn_jnts']
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

    cmds.group(n='grp_misc_ctrls',p='ctrl_COG',em=True)

    sys_attr()

    # place systems & joints into heirachy
    for type_sys in ["ik","fk"]:
        grp_list = cmds.ls(f"grp_{type_sys}_jnts_*")
        if grp_list:
            try:
                cmds.parent(grp_list,f"grp_{type_sys}_jnts")
            except RuntimeError:
                pass
        grp_ctrl_list = cmds.ls(f"grp_{type_sys}_ctrls_*")
        if grp_ctrl_list:
            try:
                cmds.parent(grp_ctrl_list,"grp_misc_ctrls")
            except RuntimeError:
                pass
    hdl_list = cmds.ls("hdl_ik_*")
    if hdl_list:
        try:
            cmds.parent(hdl_list,"grp_ik_handles")
        except RuntimeError:
            pass
    
    root_jnt = [item for item in cmds.ls("jnt_rig*") if "root" in item]
    if len(root_jnt) > 1:
        cmds.error("ERROR: More than one root object found please rename")
    else:
        cmds.parent(root_jnt, "grp_rig_jnts")

    #except RuntimeError:
    #    cmds.error("Groups exists already that matches name, grps might be missing in file structure")"""