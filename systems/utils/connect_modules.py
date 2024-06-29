import maya.cmds as cmds
from systems.utils import utils
import importlib
importlib.reload(utils)

modules_to_connect = {}
joints_to_parent = []

def attach(master_guide, selection):
    connector_list = utils.connector(master_guide, selection[0])

    if "grp_connector_clusters" in cmds.ls("grp_connector_clusters"):
        cmds.parent(connector_list,"grp_connector_clusters")
    else:
        cmds.group(connector_list,n="grp_connector_clusters",w=1)

    temp_group = [master_guide]
    modules_to_connect.update({f"{master_guide}_2_{selection[0]}": temp_group})

    return [modules_to_connect, connector_list]

def prep_attach_joints(child_joint, parent_joint):
    child_joint = cmds.listRelatives(child_joint, c=1, typ="transform")[0]

    temp_group = [f"jnt_rig_{child_joint}", f"jnt_rig_{parent_joint[0]}"]
    joints_to_parent.append(temp_group)

    return [child_joint, parent_joint[0]]

def attach_joints():
    for x in joints_to_parent:
        cmds.parent(x[0],x[1])

def connect_polished(systems_to_connect):
    ikfk_mapping = {
        "IK": "ctrl_ik",
        "FK": "ctrl_fk",
        "FKIK": ["ctrl_ik", "ctrl_fk"]
    }
    
    systems_ikfk = []
    
    for system in systems_to_connect:
        master_guide = cmds.getAttr(f"{system}.master_guide", asString=1)
        ikfk = cmds.getAttr(f"{system}.{master_guide}_rig_type", asString=1)
        mapped_value = ikfk_mapping.get(ikfk, ikfk)
        
        if isinstance(mapped_value, list):
            system_values = [f"{value}_{system}" for value in mapped_value]
        else:
            system_values = [f"{mapped_value}_{system}"]
        
        systems_ikfk.append(system_values)
    
    target, p_object = systems_ikfk

    substrings_to_check = ["COG", "root"]
    found = False
    for system in systems_to_connect:
        found_substring = utils.find_substring_in_list(system, substrings_to_check)
        if found_substring:
            found = True
            break
     
    if found == False:
        if len(target) == 2:
            constraint_1 = cmds.parentConstraint(p_object, target[0], mo=1, n=f"pConst_{p_object[0]}")
            constraint_2 = cmds.parentConstraint(p_object, target[1], mo=1, n=f"pConst_{p_object[0]}")
        elif len(target) == 1:
            constraint_1 = cmds.parentConstraint(p_object, target, mo=1, n=f"pConst_{p_object[0]}")

    if constraint_1 and constraint_2:
        return [constraint_1, constraint_2]
    else:
        return [constraint_1]
