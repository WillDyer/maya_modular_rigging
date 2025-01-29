import maya.cmds as cmds
import json
import math

dict_var_types = {
                "module": "string",
                "master_guide": "string",
                "guide_list": "list",
                "guide_scale": "float",
                "joints": "list",
                "side": "string",
                "connectors": "list",
                "system_to_connect": "list",
                "space_swap": "list",
                "ik_ctrl_list": "list",
                "fk_ctrl_list": "list",
                "ik_joint_list": "list",
                "fk_joint_list": "list",
                "rev_locators": "list",
                "guide_number": "float",
                "hidden_obj": "string",
                "hand_grp_num": "float"
            }


def setup(temp_dict, data_guide):
    if not cmds.attributeQuery("init_Data", node=data_guide, exists=True):
        cmds.addAttr(data_guide, longName="init_data", dataType='string')
    serialised_data = json.dumps(temp_dict)
    cmds.setAttr(f"{data_guide}.init_data", serialised_data, type="string")

    for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz","v"]:
        cmds.setAttr(f"{data_guide}.{attr}", cb=0,k=0,l=1)


def init_data():
    return_dict = {}
    data_guides = cmds.ls("data_*",type="transform")
    print(f"Existing Guides Found: {data_guides}")
    for guide in data_guides:
        if cmds.attributeQuery("init_data", node=guide, exists=True):
            retrieved_data = cmds.getAttr(f"{guide}.init_data")
            init_data = json.loads(retrieved_data)
            return_dict[guide] = init_data
        else:
            cmds.warning(f"guide_data: couldnt find init_data on {guide} setup wont be the same")

    return return_dict


def capture_control_data(ctrl=None, guide=None, use_associated=False):
    if use_associated is True:
        guide = cmds.getAttr(f"{ctrl}.associated_guide", asString=True)

    if cmds.attributeQuery("ctrl_data", node=guide, exists=True):
        retrieved_data = cmds.getAttr(f"{guide}.ctrl_data")
        control_data = json.loads(retrieved_data)
    else:
        control_data = {}
    
    if not cmds.objExists(ctrl):
        print(f"{ctrl} doesnt exist cant save ctrl data for this guide")
        return

    transform_data = {
        "translate": cmds.xform(ctrl, q=True, translation=True, worldSpace=True),
        "rotate": cmds.xform(ctrl, q=True, rotation=True, worldSpace=True),
        "scale": cmds.xform(ctrl, q=True, scale=True, worldSpace=True)
    }
    
    shapes = cmds.listRelatives(ctrl, shapes=True, fullPath=True) or []
    shape_data = []
    
    for shape in shapes:
        if cmds.nodeType(shape) == "nurbsCurve":
            if cmds.getAttr(shape + '.form') == 2 :
                control_points = cmds.getAttr(shape + '.cp[*]')
                control_points = [tuple(pt) for pt in control_points]  # Convert to a list of tuples
                num_points = len(control_points)
                center = [sum(coord) / num_points for coord in zip(*control_points)]
                distances = [math.dist(center, pt) for pt in control_points]
                cvs = [cmds.xform(f"{shape}.cv[{i}]", q=True, t=True, os=True)
                       for i in range(len(cmds.ls(f"{shape}.cv[*]", flatten=True)))]

                sections = cmds.getAttr(shape + '.spans')
                radius = distances[0]
                shape_data.append({
                    'type': 'circle',
                    'center': center,
                    'radius': radius,
                    'control_points': control_points,
                    'cvs': cvs,
                    'sections': sections
                    })
            else:
                cvs = [cmds.xform(f"{shape}.cv[{i}]", q=True, t=True, os=True)
                       for i in range(cmds.getAttr(f"{shape}.spans") + cmds.getAttr(f"{shape}.degree"))]
                shape_data.append({
                    "type": "nurbsCurve",
                    "cvs": cvs,
                    "degree": cmds.getAttr(f"{shape}.degree")
                    })
        elif cmds.nodeType(shape) == "mesh":
            vertices = [cmds.pointPosition(f"{shape}.vtx[{i}]", world=True) for i in range(cmds.polyEvaluate(shape, vertex=True))]
            shape_data.append({
                "type": "mesh",
                "vertices": vertices
            })
        # Add other shape types as needed

    # Store data
    control_data[ctrl] = {
        "transform": transform_data,
        "shapes": shape_data
    }

    if not cmds.attributeQuery("ctrl_data", node=guide, exists=True):
        cmds.addAttr(guide, longName="ctrl_data", dataType='string')

    serialised_data = json.dumps(control_data)
    cmds.setAttr(f"{guide}.ctrl_data", serialised_data, type="string")
    
    # return control_data
