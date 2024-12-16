import maya.cmds as cmds

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
    for key in temp_dict.keys():
        if temp_dict.keys() == "guide_number":
            cmds.addAttr(data_guide, ln=key, at="float",k=1)
            cmds.setAttr(f"{data_guide}.{key}", temp_dict[key])
        elif isinstance(temp_dict[key], str):
            cmds.addAttr(data_guide, ln=key, at="enum", en=temp_dict[key], k=1)
        elif isinstance(temp_dict[key], list):
            if len(temp_dict[key]) == 0: enum_list = "empty"
            else: enum_list = ":".join(temp_dict[key])
            cmds.addAttr(data_guide, ln=key, at="enum", en=enum_list, k=1)
        elif isinstance(temp_dict[key], float):
            cmds.addAttr(data_guide, ln=key, at="float",k=1)
            cmds.setAttr(f"{data_guide}.{key}", temp_dict[key])
        elif isinstance(temp_dict[key], int):
            cmds.addAttr(data_guide, ln=key, at="float",k=1)
            cmds.setAttr(f"{data_guide}.{key}", temp_dict[key])

    # hide in outliner:
    # cmds.setAttr(f"{data_guide}.hiddenInOutliner", True)

    for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz","v"]:
        cmds.setAttr(f"{data_guide}.{attr}", cb=0,k=0,l=1)


def init_data():
    return_dict = {}
    data_guides = cmds.ls("data_*",type="transform")
    print(f"Existing Guides Found: {data_guides}")
    for guide in data_guides:
        temp_dict = {}
        attr_list = cmds.listAttr(guide, r=1,k=1)
        for attr in attr_list:
            if dict_var_types[attr] == "guide_number": pass
            elif dict_var_types[attr] == "list":
                value_list = cmds.attributeQuery(attr, node=guide, le=1)
                value = value_list[0].split(":")
            elif dict_var_types[attr] == "string":
                value = cmds.getAttr(f"{guide}.{attr}",asString=True)
            elif dict_var_types[attr] == "float" or dict_var_types[attr] == "long":
                value = cmds.getAttr(f"{guide}.{attr}")

            if isinstance(value, list) and value[0] == "empty": value = []

            temp_dict[attr] = value
        return_dict[guide] = temp_dict
    return return_dict
