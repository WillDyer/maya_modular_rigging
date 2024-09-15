import maya.cmds as cmds
import importlib

from systems import joints
importlib.reload(joints)


class mirror_data():
    def __init__(self, systems_to_be_made, orientation):
        self.data_to_be_checked = systems_to_be_made
        self.orientation = orientation
        self.mirror_data()

    def create_mirrored_guides(self):  # Create guide locators
        tmp_guide_list = []
        for guide in self.key["guide_list"]:
            if "master" in guide:
                guide_name = f"master_{self.side}{guide[8:]}"
            else:
                guide_name = f"{self.side}{guide[1:]}"

            loc = cmds.xform(guide, r=True, ws=True, q=True, t=True)
            rot = cmds.xform(guide, r=True, ws=True, q=True, ro=True)

            tmp = cmds.spaceLocator(n=guide_name)[0]
            cmds.xform(tmp, t=loc, ro=rot)
            tmp_guide_list.append(tmp)

        grp_name = cmds.group(n="mirroring_transform", em=1)
        cmds.parent(tmp_guide_list, grp_name)
        cmds.xform(grp_name, scale=[-1,1,1])
        cmds.parent(tmp_guide_list, w=True)
        cmds.makeIdentity(tmp_guide_list[-1], apply=True, s=True)
        cmds.delete(grp_name)

        for guide in range(len(tmp_guide_list)):
            try:
                cmds.parent(tmp_guide_list[guide], tmp_guide_list[guide+1])
            except:
                pass

        self.master_guide = tmp_guide_list[-1]
        self.guide_list = tmp_guide_list

    def mirror_joints(self):
        joint_list = joints.joint("xyz",self.master_guide,system="rig")
        return joint_list

    def get_mirrored_side(self):
        if self.key["side"] == "L":
            self.side = "R"
        elif self.key["side"] == "R":
            self.side = "L"
        else:
            self.side = ""

    def get_mirrored_system_to_connect(self):  # Mirrored system to connect
        system_to_connect = self.key["system_to_connect"]
        print(system_to_connect)
        # mirrored_system_to_connect = [item.replace(f"{self.key['side']}_", self.simple_side) if f"{self.key['side']}_" in item else item for item in system_to_connect]
        mirrored_system_to_connect = []
        for item in system_to_connect:
            if f"{self.key['side']}" in item:
                mirrored_item = item.replace(f"{self.key['side']}", self.side,1)
            else:
                mirrored_item = item
            mirrored_system_to_connect.append(mirrored_item)

        return mirrored_system_to_connect

    def copy_mirrored_attrs(self):  # Copy attrs accross
        self.non_proxy_attr_list = []
        proxy_obj_list = self.guide_list
        for attr in cmds.listAttr(self.key["master_guide"], r=1,ud=1):
            if "_control_shape" in attr:
                pass
            else:
                try:
                    if attr == "master_guide":
                        cmds.addAttr(proxy_obj_list, ln="master_guide",at="enum",en=self.master_guide,k=0)
                    elif attr not in ['visibility', 'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
                        try:
                            # new_attr_name = f"master_{self.side}{attr[8:]}"
                            new_attr_name = attr.replace(f"{self.key['side']}",self.side,1)
                        except:
                            pass
                        cmds.addAttr(proxy_obj_list,ln=f"{new_attr_name}", proxy=f"{self.key['master_guide']}.{attr}")
                    else:
                        pass
                except:
                    pass

        for guide in self.key["guide_list"]:
            for attr in cmds.listAttr(guide, r=1,ud=1):
                if "_control_shape" in attr:
                    new_attr_name = attr.replace(f"{self.key['side']}",self.side,1)
                    mirrored_guide = f"{self.side}{guide[1:]}"
                    enum_value = cmds.getAttr(f"{guide}.{attr}",asString=1)
                    cmds.addAttr(mirrored_guide,ln=f"{new_attr_name}",at="enum",en=enum_value)

    def mirror_reverse_foot(self):
        try:
            if self.key["rev_locators"]:
                mirrored_rev_locators = []
                for loc in self.key["rev_locators"]:
                    new_loc_name = loc.replace(f"{self.key['side']}",self.side,1)
                    cmds.duplicate(loc, n=new_loc_name)
                    mirrored_rev_locators.append(new_loc_name)

                cmds.group(n="tmp_mirror",em=1)
                cmds.parent(mirrored_rev_locators, "tmp_mirror")
                cmds.setAttr("tmp_mirror.scaleX",-1)
                cmds.parent(mirrored_rev_locators,w=1)
                cmds.delete("tmp_mirror")

                return mirrored_rev_locators
            else:
                return None
        except KeyError:
            return None

    def mirror_data(self):
        temp_systems_to_be_made = {}
        for key in self.data_to_be_checked.values():
            self.locator_list = []
            mirror_attribute = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts", asString=1)
            if mirror_attribute == "Yes":  # YES
                self.key = key
                self.get_mirrored_side()
                self.create_mirrored_guides()
                self.copy_mirrored_attrs()
                self.joint_list = self.mirror_joints()
                self.mirrored_system_to_connect = self.get_mirrored_system_to_connect()
                self.mirrored_rev_locators = self.mirror_reverse_foot()

                temp_dict = {
                    "module": key["module"],
                    "master_guide": self.master_guide,
                    "guide_list": self.guide_list,
                    "guide_scale": key["guide_scale"],
                    "joints": self.joint_list,
                    "side": self.side,
                    "connectors": [],
                    "system_to_connect": self.mirrored_system_to_connect,
                    "space_swap": key["space_swap"],
                    "ik_ctrl_list": [],
                    "fk_ctrl_list": [],
                    "ik_joint_list": [],
                    "fk_joint_list": []
                }

                if self.mirrored_rev_locators:
                    temp_dict.update({"rev_locators": self.mirrored_rev_locators})

                temp_systems_to_be_made[self.master_guide] = temp_dict

        self.data_to_be_checked.update(temp_systems_to_be_made)

    def get_mirror_data(self):
        return self.data_to_be_checked
