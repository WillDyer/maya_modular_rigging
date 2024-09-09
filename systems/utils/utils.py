import maya.cmds as cmds
from PySide2.QtWidgets import *


def create_cube(name, scale):
    ctrlCV = cmds.curve(n=name,d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                      (0,1,0),(1,1,0),(1,0,0),(1,1,0),
                                      (1,1,1),(1,0,1),(1,1,1),
                                      (0,1,1),(0,0,1),(0,1,1),(0,1,0)])

    cmds.CenterPivot()
    cmds.xform(ctrlCV,t=(-.5,-.5,-.5))
    cmds.xform(ctrlCV,s=[scale[0],scale[1],scale[2]])
    cmds.select(ctrlCV)
    cmds.FreezeTransformations()
    cmds.delete(ctrlCV, ch=1)
    return ctrlCV


def connector(first_jnt, second_jnt):
    first_point_loc = cmds.xform(first_jnt,q=1,ws=1,rp=1)
    second_point_loc = cmds.xform(second_jnt,q=1,ws=1,rp=1)
    cmds.curve(d=1, p=[first_point_loc, second_point_loc], n="connector_curve_" + first_jnt)
    cluster_1 = cmds.cluster(f"connector_curve_{first_jnt}.cv[0]", n="cluster_" + first_jnt + "_cv0")
    cluster_2 = cmds.cluster(f"connector_curve_{first_jnt}.cv[1]", n="cluster_" + second_jnt + "_cv1")
    cmds.parent(cluster_1[1], first_jnt)
    cmds.parent(cluster_2[1], second_jnt)
    for x in cmds.ls(typ="cluster"):
        cmds.hide(f"{x}Handle")
        cmds.setAttr(f"{x}Handle.hiddenInOutliner", True)
    cmds.setAttr(f"connector_curve_{first_jnt}.template", 1)

    curve = f"connector_curve_{first_jnt}"
    return curve


def constraint_from_lists_1to1(list_1, list_2, maintain_offset):
    for x in range(len(list_1)):
        if "root" in list_2[x]:
            pass
        else:
            cmds.parentConstraint(list_1[x], list_2[x],mo=maintain_offset, n=f"pConst_{list_1[x]}")


def constraint_from_lists_2to1(list_1, list_2, base_list, maintain_offset):
    for x in range(len(list_1)):
        if "root" in list_2[x]:
            pass
        else:
            cmds.parentConstraint(list_1[x], list_2[x], base_list[x], mo=maintain_offset, n=f"pConst_{list_1[x]}")


def find_substring_in_list(string, substrings):
    for substring in substrings:
        if substring in string:
            return substring
    return None


def colour_controls(ctrl_list,colour_dict):
    def set_drawing_override_color(nurbs_curve, rgb_colour,side):
        if side == "None": colour = rgb_colour["root"]
        elif side == "l": colour = rgb_colour["L_colour"]
        elif side == "r": colour = rgb_colour["R_Colour"]
        elif side == "default": colour = rgb_colour["C_colour"]
        else: colour = rgb_colour["C_colour"]
        colour = [c / 255.0 for c in colour]
        cmds.setAttr(f"{nurbs_curve}.overrideEnabled", 1)
        cmds.setAttr(f"{nurbs_curve}.overrideRGBColors", 1)
        cmds.setAttr(f"{nurbs_curve}.overrideColorR", colour[0])
        cmds.setAttr(f"{nurbs_curve}.overrideColorG", colour[1])
        cmds.setAttr(f"{nurbs_curve}.overrideColorB", colour[2])
    # COLOR_CONFIG = {'l': 6, 'r': 13, 'default': 22}
    for ctrl in ctrl_list:
        try:
            if ctrl == "ctrl_root":
                set_drawing_override_color(ctrl, colour_dict,side="None")
            elif ctrl[:4] == "ctrl":
                side = ctrl.split("_")[-2]
                try:
                    set_drawing_override_color(ctrl, colour_dict, side)
                except KeyError:
                    set_drawing_override_color(ctrl, colour_dict, side="default")
                    pass
            else:
                pass
        except:
            pass


def get_joints_between(start_joint, end_joint):
    # Ensure both joints exist
    if not cmds.objExists(start_joint) or not cmds.objExists(end_joint):
        raise ValueError("One or both of the specified joints do not exist.")

    # Get the full path for both joints
    start_path = cmds.ls(start_joint, long=True)[0]
    end_path = cmds.ls(end_joint, long=True)[0]

    # Split the paths into individual joint names
    start_joints = start_path.split('|')[1:]  # Exclude the root '|'
    end_joints = end_path.split('|')[1:]      # Exclude the root '|'

    # Find the common ancestor
    common_ancestor = None
    for sj, ej in zip(start_joints, end_joints):
        if sj == ej:
            common_ancestor = sj
        else:
            break

    if common_ancestor is None:
        raise ValueError("The specified joints do not share a common ancestor.")

    # Build the path from start_joint to common_ancestor
    start_to_common = start_joints[start_joints.index(common_ancestor):]

    # Build the path from common_ancestor to end_joint (reverse order)
    common_to_end = end_joints[end_joints.index(common_ancestor)+1:]

    # Combine the paths
    joint_path = start_to_common + common_to_end

    return joint_path


def hide_guides(systems_to_be_made, created_guides, module_widget, hidden):
    if hidden is True:
        for key in systems_to_be_made.values():
            cmds.hide(key["master_guide"])
            cmds.setAttr(f"{key['master_guide']}.hiddenInOutliner", True)
        cmds.hide("grp_connector_clusters")
    else:
        for key in systems_to_be_made.values():
            cmds.showHidden(key["master_guide"])
            cmds.setAttr(f"{key['master_guide']}.hiddenInOutliner", False)
        cmds.showHidden("grp_connector_clusters")
        for module in created_guides:
            pushButton = module_widget.findChild(QPushButton, f"button_remove_{module}")
            pushButton.setEnabled(True)


def delete_guides(systems_to_be_made, systems_to_be_deleted_polished):
    for key in systems_to_be_made.values():
        cmds.delete(key["master_guide"])
    cmds.delete("grp_connector_clusters")
    if len(systems_to_be_deleted_polished) > 0:
        cmds.delete(systems_to_be_deleted_polished)
    grp_reverse_foot_guides = cmds.ls("grp_rev_loc_*")
    if len(grp_reverse_foot_guides) > 0:
        cmds.delete(grp_reverse_foot_guides)


def delete_joints(systems_to_be_made, skn_jnt_list):
    for key in systems_to_be_made.values():
        try: cmds.delete(key["joints"])
        except: ValueError  # catches if the joints already been deleted
    try: cmds.delete(skn_jnt_list)
    except: ValueError  # catches if the joints already been deleted
