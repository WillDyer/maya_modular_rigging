import maya.cmds as cmds
from systems.utils import utils
import importlib
importlib.reload(utils)

modules_to_connect = {}

def attach(master_guide, selection):
    connector_list = utils.connector(master_guide, selection[0])

    if "grp_connector_clusters" in cmds.ls("grp_connector_clusters"):
        cmds.parent(connector_list,"grp_connector_clusters")
    else:
        cmds.group(connector_list,n="grp_connector_clusters",w=1)

    temp_group = [master_guide]
    modules_to_connect.update({f"{master_guide}_2_{selection[0]}": temp_group})

    return [modules_to_connect, connector_list]

joints_to_parent = []

def prep_attach_joints(child_joint, parent_joint):
    child_joint = cmds.listRelatives(child_joint, c=1, typ="transform")[0]

    temp_group = [f"jnt_rig_{child_joint}", f"jnt_rig_{parent_joint[0]}"]
    joints_to_parent.append(temp_group)

def attach_joints():
    for x in joints_to_parent:
        cmds.parent(x[0],x[1])

    
