import maya.cmds as cmds
import importlib


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
    'rig_system': ['Rig System','Shown:Hidden',False,True,'grp_rig_joints.visibility'],
    'skn_system': ['Skin System','Shown:Hidden',False,True,'grp_skn_joints.visibility'],
    'fk_system': ['FK System','Shown:Hidden',False,True,'grp_fk_joints.visibility'],
    'ik_system': ['IK System','Shown:Hidden',False,True,'grp_ik_joints.visibility'],
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


def grpSetup():
    selection = cmds.ls(sl=True, typ='joint')
    ABC_FILE = "./imports/curve_import.abc"

    try:
        cmds.file(ABC_FILE, i=True)
    except RuntimeError:
        print("Couldnt load file using basic shapes instead")
        cmds.circle(n="ctrl_root",r=50,nr=(0, 1, 0))
        cmds.circle(n="ctrl_COG",r=25,nr=(0, 1, 0))

    #try:
        grpList = ['grp_mesh','grp_controls','grp_joints','grp_locators','grp_blendshapes']
        jntList = ['grp_ik_handles','grp_ik_joints','grp_fk_joints','grp_rig_joints','grp_skn_joints']
        # ctrlList = ['grp_ctrls_head','grp_ctrls_spine','grp_ctrls_arms','grp_ctrls_legs']
    
        cmds.group(n='WD_Rig_Master',w=True,em=True)

        cmds.group(n="grp_rig", p="WD_Rig_Master",em=True)
        cmds.group(n='DO_NOT_TOUCH',p='WD_Rig_Master',em=True)
    
        for x in range(len(grpList)):
            cmds.group(n=grpList[x],p="grp_rig",em=True)
        for x in range(len(jntList)):
            cmds.group(n=jntList[x],p=grpList[2],em=True)
        
        cmds.group(n='grp_root',p='grp_controls',em=True)
        cmds.parent('ctrl_root','grp_root')
        cmds.group(n='grp_COG',p='ctrl_root',em=True)
        if "jnt_rig_COG" in cmds.ls("jnt_rig_COG"):
            cmds.matchTransform('grp_COG','jnt_rig_COG',pos=True,rot=True)

        cmds.matchTransform('ctrl_COG','grp_COG',pos=True,rot=True)
        cmds.parent('ctrl_COG','grp_COG')

        cmds.group(n='grp_misc_ctrls',p='ctrl_COG',em=True)

        # for x in range(len(ctrlList)):
        #     cmds.group(n=ctrlList[x],p='ctrl_COG',em=True)
        #spine grps
        # cmds.group(n='grp_ik_spine',p='grp_ctrls_spine',em=True)
        # cmds.group(n='grp_fk_spine',p='grp_ctrls_spine',em=True)
    
        #arm groups
        # cmds.group(n='grp_clav_rotate',p='grp_ctrls_arms',em=True)
        # cmds.group(n='grp_ik_arm',p='grp_clav_rotate',em=True)
        # cmds.group(n='grp_fk_arm',p='grp_clav_rotate',em=True)
    
        #leg groups
        # cmds.group(n='grp_ik_leg',p='grp_ctrls_legs',em=True)
        # cmds.group(n='grp_fk_leg',p='grp_ctrls_legs',em=True)

        sys_attr()

    #except RuntimeError:
    #    cmds.error("Groups exists already that matches name, grps might be missing in file structure")