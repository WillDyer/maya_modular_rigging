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


def prep_attach_joints(child_joint, parent_joint, need_child):
    if need_child:
        child_joint = cmds.listRelatives(child_joint, c=1, typ="transform")[0]

    temp_group = [f"jnt_rig_{child_joint}", f"jnt_rig_{parent_joint[0]}"]
    joints_to_parent.append(temp_group)

    return [child_joint, parent_joint[0]]


def attach_joints(systems_to_be_made, system):
    to_parent = [key["system_to_connect"] for key in systems_to_be_made.values() if key["system_to_connect"]]
    for x in to_parent:
        cmds.parent(f"jnt_{system}_{x[0]}",f"jnt_{system}_{x[1]}")


def connect_to_ikfk_switch(p_object, constraint):
    for x in p_object:
        attr_exists = cmds.attributeQuery('ikfk_switch_name', node=x, exists=True)
        if attr_exists:
            ikfk_switch_name = cmds.getAttr(f"{x}.ikfk_switch_name",asString=1)
            try:
                reverse_node = cmds.createNode('reverse', n=f"{ikfk_switch_name}_Reverse_#")
                cmds.connectAttr(f"{x}.{ikfk_switch_name}",f"{reverse_node}.inputX")
                cmds.connectAttr(f"{reverse_node}.outputX",f"{constraint[0]}.{x}W0")
            except:pass
            try: cmds.connectAttr(f"{x}.{ikfk_switch_name}",f"{constraint[0]}.{x}W1")
            except: pass


def connect_polished(systems_to_connect):
    ikfk_mapping = {
        "IK": "offset_ik",
        "FK": "offset_fk",
        "FKIK": ["offset_ik", "offset_fk"],
        "IK_Ribbon": "jnt_ik"
    }

    systems_ikfk = []

    for system in systems_to_connect:
        master_guide = cmds.getAttr(f"{system}.master_guide", asString=1)
        ikfk = cmds.getAttr(f"{system}.{master_guide}_rig_type", asString=1)
        mapped_value = ikfk_mapping.get(ikfk, ikfk)

        if isinstance(mapped_value, list):
            # system_values = [f"{value}_{system}" for value in mapped_value]
            system_values = []
            for value in mapped_value:
                if not cmds.ls(f"{value}_{system}"):
                    value = value.replace("offset_","ctrl_")
                    system_values.append(f"{value}_{system}")
                else: system_values.append(f"{value}_{system}")

        else:
            if not cmds.ls(f"{mapped_value}_{system}"):
                mapped_value = mapped_value.replace("offset_","ctrl_")
                system_values = [f"{mapped_value}_{system}"]
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

    if found is False:
        if len(target) == 2:
            constraint_1 = cmds.parentConstraint(p_object, target[0], mo=1, n=f"pConst_{p_object[0]}")
            connect_to_ikfk_switch(p_object, constraint_1)
            constraint_2 = cmds.parentConstraint(p_object, target[1], mo=1, n=f"pConst_{p_object[0]}")
            connect_to_ikfk_switch(p_object, constraint_2)
            return [constraint_1, constraint_2]
        elif len(target) == 1:
            constraint_1 = cmds.parentConstraint(p_object, target, mo=1, n=f"pConst_{p_object[0]}")
            connect_to_ikfk_switch(p_object, constraint_1)
            return [constraint_1]
