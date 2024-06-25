import maya.cmds as cmds
import importlib
import sys
import os
from systems.utils import (cube_crv, connect_modules, utils)
importlib.reload(connect_modules)
importlib.reload(utils)

scale = 1

def guides(accessed_module, offset,side):
    selection = cmds.ls(sl=1)
    if selection:
        if "master" in selection[0]:
            cmds.warning("Cant attach a new module to a master control please select a guide.")
        elif "master" not in selection[0]:
            guide = creation(accessed_module,offset,side)
            master_guide = guide[0]
            connect_modules.attach(master_guide, selection)
            connect_modules.prep_attach_joints(master_guide, selection)
            print("Attaching to module.")
            return guide
    else:
        guide = creation(accessed_module,offset,side)
        return guide


def creation(accessed_module,offset,side):
    connector_list = []
    module = importlib.import_module(f"systems.modules.{accessed_module}")
    importlib.reload(module)
    ABC_FILE = f"{os.path.dirname(os.path.abspath(__file__))}\imports\guide_shape.abc"
    COLOR_CONFIG = {'l': 6, 'r': 13, 'default': 22}
    guide_list = []
    root_exists = False

    if module.side == "None":
        side = ""
    else:
        side = module.side

    # create master guide for module
    if "root" in module.system:
        master_guide = "root"
    else:
        master_guide = cube_crv.create_cube(f"master_{accessed_module}{side}_#",scale=[5,5,5])
        pos = module.system_pos[module.system[0]]
        rot = module.system_rot[module.system[0]]
        cmds.xform(master_guide,ws=1,t=[pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2]])
        cmds.xform(master_guide,ws=1,ro=[rot[0],rot[1],rot[2]])


    for x in module.system:
        # Import custom guide crv if fails use locator
        try:
            if "root" in x:
                imported = cmds.circle(r=50,nr=[0,1,0])
                root_exists = True
                guide = cmds.rename(imported[0], f"{x}{side}")
            else:
                imported = cmds.file(ABC_FILE, i=1,namespace="test",rnn=1)
                guide = cmds.rename(imported[0], f"{x}{side}_#")
            if "root" in x and root_exists == True:
                master_guide = guide
            else:
                guide_list.append(guide)
            for shape in imported[1:]:
                shape = shape.split("|")[-1]
                cmds.rename(shape, f"{guide}_shape_#")

            cmds.setAttr(f"{guide}.overrideEnabled",1)
            cmds.setAttr(f"{guide}.overrideColor",COLOR_CONFIG["default"])
        except RuntimeError:
            print("Couldnt load file using basic shapes instead")
            cmds.spaceLocator(n=x)

        # set location of guide crvs then OPM
        pos = module.system_pos[x]
        rot = module.system_rot[x]
        cmds.xform(guide,ws=1,t=[pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2]])
        cmds.xform(guide,ws=1,ro=[rot[0],rot[1],rot[2]])

    # parent together
    guide_list.reverse()
    guide_list.append(master_guide)
    for x in range(len(guide_list)):
        try:
            cmds.parent(guide_list[x],guide_list[x+1])
            connector = utils.connector(guide_list[x],guide_list[x+1])
            connector_list.append(connector)
            
        except:
            pass # end of list

    if "grp_connector_clusters" in cmds.ls("grp_connector_clusters"):
        cmds.parent(connector_list,"grp_connector_clusters")
    else:
        cmds.group(connector_list,n="grp_connector_clusters",w=1)

    add_custom_attr(guide_list, master_guide)
    cmds.addAttr(master_guide, ln="is_master",at="enum",en="True",k=0) # adding master group attr
    cmds.addAttr(master_guide, ln="base_module",at="enum",en=accessed_module,k=0) # module attr
    cmds.addAttr(master_guide, ln="module_side",at="enum",en=side,k=0) # module side
    for item in ["is_master","base_module","module_side"]:
        cmds.addAttr(guide_list[:-1],ln=f"{item}", proxy=f"{guide_list[-1]}.{item}")
    return [master_guide, connector_list]

def add_custom_attr(system, master_guide):
    custom_attrs = {"module_dvdr": ["enum","------------","MODULE",True],
                    "skeleton_dvdr": ["enum","------------", "SKELETON",True],
                    "mirror_jnts": ["enum","Mirror Joints", "No:Yes",False],
                    "twist_jnts": ["enum","Twist Joints", "Yes:No",False],
                    "twist_amount": ["float","Twist Amount", "UPDATE",False],
                    "rig_dvdr": ["enum","------------","RIG",True],
                    "rig_type": ["enum","Rig Type","FK:IK:FKIK",False],
                    "squash_stretch": ["enum","Squash Stech","No:Yes",False]
                    }

    for i in custom_attrs:
        if custom_attrs[i][0] == "enum":
            cmds.addAttr(master_guide,k=1,ln=f"{system[-1]}_{i}",nn=custom_attrs[i][1],at="enum",en=custom_attrs[i][2])
        elif custom_attrs[i][0] == "float":
            cmds.addAttr(master_guide,k=1,ln=f"{system[-1]}_{i}",nn=custom_attrs[i][1],at="float",min=0)
        if custom_attrs[i][3] == True:
            cmds.setAttr(f"{master_guide}.{system[-1]}_{i}", l=1)

    for item in custom_attrs:
        cmds.addAttr(system[:-1],ln=f"{system[-1]}_{item}", proxy=f"{system[-1]}.{system[-1]}_{item}")