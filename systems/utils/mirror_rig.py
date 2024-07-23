import maya.cmds as cmds


class mirror_data():
    def __init__(self, systems_to_be_made):
        self.data_to_be_checked = systems_to_be_made
        self.mirror_data()

    def mirror_joints(self):
        cmds.select(self.key["joints"][0])
        joint_list = cmds.mirrorJoint(mirrorYZ=True,mirrorBehavior=True,searchReplace=('_l_', '_r_'))
        return joint_list

    def get_mirrored_side(self):
        if self.key["side"] == "_l":
            self.side = "_r"
            self.simple_side = "_r_"
        elif self.key["side"] == "_r":
            self.side = "_l"
            self.simple_side = "_l_"
        else:
            self.side = ""

    def get_mirrored_system_to_connect(self):  # Mirrored system to connect
        system_to_connect = self.key["system_to_connect"]
        mirrored_system_to_connect = [item.replace(f"{self.key['side']}_", self.simple_side) if f"{self.key['side']}_" in item else item for item in system_to_connect]
        return mirrored_system_to_connect

    def create_mirrored_guides(self):  # Create guide locators
        for jnt in self.joint_list:
            for type in ["jnt_rig_","jnt_ik_","jnt_fk_"]:
                if type in jnt:
                    tmp_jnt = jnt.replace(type, "")
            locator_name = cmds.spaceLocator(n=tmp_jnt)
            cmds.matchTransform(locator_name, jnt)
            self.locator_list.append(locator_name[0])
        self.locator_list.reverse()
        for locator in range(len(self.locator_list)):
            try:
                cmds.parent(self.locator_list[locator], self.locator_list[locator+1])
            except:
                pass

    def create_mirrored_master_guide(self):  # Create master guide
        split_master_guide = self.key["master_guide"].split("_")
        master_guide = self.key["master_guide"].replace(f"_{split_master_guide[-2]}_",self.simple_side)
        self.proxy_obj_list = self.locator_list
        if "master" in master_guide:
            cmds.spaceLocator(n=master_guide)
            cmds.matchTransform(master_guide,self.joint_list[0])
            cmds.parent(self.locator_list[-1],master_guide)

            self.proxy_obj_list.append(master_guide)
        return master_guide

    def copy_mirrored_attrs(self):  # Copy attrs accross
        self.non_proxy_attr_list = []
        for attr in cmds.listAttr(self.key["master_guide"], r=1,ud=1):
            if "_control_shape" in attr:
                pass
            else:
                try:
                    if attr == "master_guide":
                        cmds.addAttr(self.proxy_obj_list, ln="master_guide",at="enum",en=self.master_guide,k=0)
                    elif attr not in ['visibility', 'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
                        try:
                            new_attr_name = attr.replace(f"{self.key['side']}_",self.simple_side,1)
                        except:
                            pass
                        cmds.addAttr(self.proxy_obj_list,ln=f"{new_attr_name}", proxy=f"{self.key['master_guide']}.{attr}")
                    else:
                        pass
                except:
                    pass

        for guide in self.key["guide_list"]:
            for attr in cmds.listAttr(guide, r=1,ud=1):
                if "_control_shape" in attr:
                    new_attr_name = attr.replace(f"{self.key['side']}_",self.simple_side,1)
                    mirrored_guide = guide.replace(f"{self.key['side']}_",self.simple_side,1)
                    enum_value = cmds.getAttr(f"{guide}.{attr}",asString=1)
                    cmds.addAttr(mirrored_guide,ln=f"{new_attr_name}",at="enum",en=enum_value)

    def mirror_reverse_foot(self):
        try:
            if self.key["rev_locators"]:
                mirrored_rev_locators = []
                for loc in self.key["rev_locators"]:
                    new_loc_name = loc.replace(f"{self.key['side']}_",self.simple_side,1)
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
                self.joint_list = self.mirror_joints()
                self.get_mirrored_side()
                self.mirrored_system_to_connect = self.get_mirrored_system_to_connect()
                self.create_mirrored_guides()
                self.master_guide = self.create_mirrored_master_guide()
                self.copy_mirrored_attrs()
                self.mirrored_rev_locators = self.mirror_reverse_foot()

                temp_dict = {
                    "module": key["module"],
                    "master_guide": self.master_guide,
                    "guide_list": self.locator_list,
                    "scale": key["scale"],
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
