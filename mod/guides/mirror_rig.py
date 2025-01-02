import maya.cmds as cmds
import importlib
import os

from mod.rig.systems import joints
from mod.rig.utils import utils
from mod.guides import guide_data
importlib.reload(joints)
importlib.reload(utils)


class mirror_data():
    def __init__(self, systems_to_be_made, orientation):
        self.data_to_be_checked = systems_to_be_made
        self.orientation = orientation
        self.mirror_data()

    def create_mirrored_guides(self):  # Create guide locators
        ABC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),"imports","guide_shape.abc")
        tmp_guide_list = []
        connector_list = []
        for guide in self.key["guide_list"]:
            loc = cmds.xform(guide, ws=True, q=True, t=True)
            rot = cmds.xform(guide, ws=True, q=True, ro=True)

            if "master" in guide:
                guide_name = f"master_{self.side}{guide[8:]}"
                imported_guide = utils.create_cube(guide_name, scale=[5,5,5])
            else:
                guide_name = f"{self.side}{guide[1:]}"
                # tmp = cmds.spaceLocator(n=guide_name)[0]
                tmp = cmds.file(ABC_FILE, i=1, namespace="test", rnn=1)
                imported_guide = cmds.rename(tmp[0], guide_name)
                cmds.setAttr(f"{imported_guide}.overrideEnabled", 1)
                cmds.setAttr(f"{imported_guide}.overrideColor", 22)
                for shape in tmp[1:]:
                    shape = shape.split("|")[-1]
                    cmds.rename(shape, f"{guide}_shape_#")

            cmds.xform(imported_guide, t=loc, ro=rot)
            tmp_guide_list.append(imported_guide)

        grp_name = cmds.group(n="mirroring_transform", em=1)
        cmds.parent(tmp_guide_list, grp_name)
        cmds.xform(grp_name, scale=[-1,1,1])
        cmds.parent(tmp_guide_list, w=True)
        cmds.makeIdentity(tmp_guide_list, apply=True, s=True)
        cmds.delete(grp_name)

        for guide in range(len(tmp_guide_list)):
            try:
                cmds.parent(tmp_guide_list[guide], tmp_guide_list[guide+1])
                connector = utils.connector(tmp_guide_list[guide], tmp_guide_list[guide+1])
                connector_list.append(connector)
            except:
                pass

        if "grp_connector_clusters" in cmds.ls("grp_connector_clusters"):
            cmds.parent(connector_list, "grp_connector_clusters")
        else:
            cmds.group(connector_list, n="grp_connector_clusters",w=1)
            cmds.setAttr("grp_connector_clusters.hiddenInOutliner", True)

        self.master_guide = tmp_guide_list[-1]
        self.guide_list = tmp_guide_list

        # create data guide
        if "root" in self.module.system or "proximal" in self.module.system: data_guide_name = f"data_{self.master_guide}"
        else: data_guide_name = self.master_guide.replace("master_", "data_")
        self.data_guide = cmds.spaceLocator(n=data_guide_name)[0]
        cmds.matchTransform(self.data_guide, self.master_guide)
        cmds.parent(self.data_guide, self.master_guide)

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

                cmds.group(mirrored_rev_locators, n=f"grp_{mirrored_rev_locators[3]}")

                return mirrored_rev_locators
            else:
                return None
        except KeyError:
            return None

    def mirror_data(self):
        temp_systems_to_be_made = {}
        for key in self.data_to_be_checked.values():
            self.locator_list = []
            accessed_module = key["module"]
            self.module = importlib.import_module(f"mod.modules.{accessed_module}")
            importlib.reload(self.module)
            mirror_attribute = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts", asString=1)
            if mirror_attribute == "Yes":  # YES
                print(f"mirroing: {key['master_guide']}")
                self.key = key
                self.get_mirrored_side()
                self.create_mirrored_guides()
                self.copy_mirrored_attrs()
                # self.joint_list = self.mirror_joints()
                self.mirrored_system_to_connect = self.get_mirrored_system_to_connect()
                self.mirrored_rev_locators = self.mirror_reverse_foot()

                temp_dict = {
                    "module": key["module"],
                    "master_guide": self.master_guide,
                    "guide_list": self.guide_list,
                    "guide_scale": key["guide_scale"],
                    "joints": [],  # self.joint_list,
                    "side": self.side,
                    "connectors": [],
                    "system_to_connect": self.mirrored_system_to_connect,
                    "space_swap": key["space_swap"],
                    "ik_ctrl_list": [],
                    "fk_ctrl_list": [],
                    "ik_joint_list": [],
                    "fk_joint_list": [],
                    "hidden_obj": self.master_guide
                }

                if self.mirrored_rev_locators:
                    temp_dict.update({"rev_locators": self.mirrored_rev_locators})
                
                if key["module"] == "hand":
                    temp_dict.update({"hand_grp_num": key['hand_grp_num']})

                temp_systems_to_be_made[self.master_guide] = temp_dict

                # cmds.setAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts", 0)
                guide_data.setup(temp_dict, self.data_guide)

        self.data_to_be_checked.update(temp_systems_to_be_made)
        
        for key in self.data_to_be_checked.values():
            if cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts", asString=1) == "Yes":
                cmds.setAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts", 0)

    def get_mirror_data(self):
        return self.data_to_be_checked
