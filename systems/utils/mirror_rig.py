import maya.cmds as cmds
import importlib

def collect_mirror_data(systems_to_be_made):
    temp_systems_to_be_made = {}
    for key in systems_to_be_made.values():
        locator_list = []
        mirror_attribute = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts", asString=1)
        if mirror_attribute == "Yes": # YES
            cmds.select(key["joints"][0])
            joint_list = cmds.mirrorJoint(mirrorYZ=True,mirrorBehavior=True,searchReplace=('_l_', '_r_'))

            if key["side"] == "_l":
                side = "_r"
                simple_side = "_r_"
            elif key["side"] == "_r":
                side = "_l"
                simple_side = "_l_"
            else:
                side = ""

            # Create guide locators
            for jnt in joint_list:

                for type in ["jnt_rig_","jnt_ik_","jnt_fk_"]:
                    if type in jnt:
                        tmp_jnt = jnt.replace(type, "")
                locator_name = cmds.spaceLocator(n=tmp_jnt)
                cmds.matchTransform(locator_name, jnt)
                locator_list.append(locator_name[0])
            locator_list.reverse()
            for locator in range(len(locator_list)):
                try:
                    cmds.parent(locator_list[locator], locator_list[locator+1])
                except:
                    pass

            # Create master guide
            split_master_guide = key["master_guide"].split("_")
            master_guide = key["master_guide"].replace(f"_{split_master_guide[-2]}_",simple_side)
            cmds.spaceLocator(n=master_guide)
            cmds.matchTransform(master_guide,joint_list[0])
            cmds.parent(locator_list[-1],master_guide)

            # Copy attrs accross
            for attr in cmds.listAttr(key["master_guide"], r=1,ud=1):
                try:
                    if not attr in ['visibility', 'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
                        try:
                            new_attr_name = attr.replace(f"{key['side']}_",simple_side,1)
                        except:
                            pass
                        cmds.addAttr(master_guide,ln=f"{new_attr_name}", proxy=f"{key['master_guide']}.{attr}")
                    else:
                        pass
                except:
                    pass

            temp_dict = {
                "module": key["module"],
                "master_guide": master_guide,
                "joints": joint_list,
                "side": side
            }
            temp_systems_to_be_made[master_guide] = temp_dict

    systems_to_be_made.update(temp_systems_to_be_made)

    return systems_to_be_made
