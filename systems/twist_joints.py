import maya.cmds as cmds
import importlib
from systems.utils import OPM, utils

importlib.reload(OPM)
importlib.reload(utils)


class PrepSkeleton():
    def __init__(self,orientation,key,system):
        self.orientation = orientation
        self.key = key
        self.system = system
        self.module = importlib.import_module(self.key['module'])
        importlib.reload(self.module)
        try:
            if self.module.twist_joint:
                for guide in self.key["guide_list"]:
                    rig_joint = f"jnt_{system}_{guide}"
                    if self.module.twist_joint["start"] in rig_joint:
                        start_joint = rig_joint
                    elif self.module.twist_joint["end"] in rig_joint:
                        end_joint = rig_joint

                self.joint_list = utils.get_joints_between(start_joint, end_joint)
                self.create_tween_joints()
        except AttributeError:
            self.return_data_list = None  # self.module.twist_joint doesnt exist

    def create_tween_joints(self):
        self.return_data_list = []
        for x in range(len(self.joint_list)):
            try:
                self.joint1 = self.joint_list[x]
                self.joint2 = self.joint_list[x+1]
                num_joints = cmds.getAttr(f"{self.key['master_guide']}.{self.key['master_guide']}_twist_amount")
                num_joints = int(num_joints)
                self.tween_joint_list = self.insert_joints_between(num_joints)
                self.twist_joint_dict = {
                    "joint1": self.joint1,
                    "joint1_twist": self.joint1_twist,
                    "joint2": self.joint2,
                    "joint2_twist": self.joint2_twist,
                    "tween_joints": self.tween_joint_list
                }

                self.return_data_list.extend(self.tween_joint_list)
                self.return_data_list.append(self.joint1_twist)
                self.return_data_list.append(self.joint2_twist)

                for joint in self.return_data_list:
                    cmds.setAttr(f"{joint}.radius", 0.5*self.module.guide_scale)

                CreateTwist(self.twist_joint_dict, self.system, self.key)
            except IndexError:
                pass

    def insert_joints_between(self, num_joints):
        if num_joints <= 0:
            return
        tween_joint_list = []

        # Get the positions of the existing joints
        pos1 = cmds.xform(self.joint1, q=True, ws=True, t=True)
        pos2 = cmds.xform(self.joint2, q=True, ws=True, t=True)

        # Calculate the step increment for each joint
        step = [(pos2[0] - pos1[0]) / (num_joints + 1),
                (pos2[1] - pos1[1]) / (num_joints + 1),
                (pos2[2] - pos1[2]) / (num_joints + 1)]

        # Create and position the new joints
        previous_joint = self.joint1
        for i in range(1, num_joints + 1):
            new_position = [pos1[0] + step[0] * i,
                            pos1[1] + step[1] * i,
                            pos1[2] + step[2] * i]
            joint1_split = self.joint1.split("_")
            joint1_split.insert(2, f"tween{i}")
            joint_name = '_'.join(joint1_split)
            cmds.joint(p=new_position,n=joint_name)
            if i == 1:
                first_joint = joint_name
            tween_joint_list.append(joint_name)
            previous_joint = joint_name

        # Reparent the final joint to joint2
        cmds.parent(self.joint2, previous_joint)
        cmds.parent(first_joint, self.joint1)
        mirror_attribute = cmds.getAttr(f"{self.key['master_guide']}.mirror_orientation", asString=1)
        if mirror_attribute == "Yes": sao_axis = f"{self.orientation[0]}down"
        else: sao_axis = f"{self.orientation[0]}up"
        cmds.joint(first_joint, edit=True, zso=1, oj="xyz", sao=sao_axis, ch=True)

        cmds.parent(self.joint2, self.joint1)

        for joint in tween_joint_list:
            cmds.parent(joint, w=True)

        # twist joint1 & joint2
        self.joint1_twist = f"{self.joint1}_twist"
        cmds.duplicate(self.joint1, parentOnly=True, n=self.joint1_twist)
        parent_joint = cmds.listRelatives(f"{self.joint1}_twist", parent=True)
        if parent_joint: cmds.parent(f"{self.joint1}_twist", w=True)
        joint2_split = self.joint1.split("_")
        joint2_split.insert(2, f"tween{num_joints + 1}")
        self.joint2_twist = '_'.join(joint2_split)
        cmds.duplicate(self.joint2, parentOnly=True, n=self.joint2_twist)
        cmds.parent(self.joint2_twist, w=True)
        # tween_joint_list.append(joint2_twist)

        # parenting
        for joint in tween_joint_list:
            cmds.parent(joint, self.joint1_twist)
        cmds.parent(self.joint2_twist, self.joint1_twist)

        return tween_joint_list

    def return_data(self):
        return self.return_data_list


class CreateTwist():
    def __init__(self, twist_joint_dict, system, key):
        self.system = system
        self.key = key
        # unpack dictionary
        self.joint1 = twist_joint_dict["joint1"]
        self.joint1_twist = twist_joint_dict["joint1_twist"]
        self.joint2 = twist_joint_dict["joint2"]
        self.joint2_twist = twist_joint_dict["joint2_twist"]
        self.tween_joints = twist_joint_dict["tween_joints"]

        if system == "rig":
            self.ik_handle()
            self.correct_orientation()
            self.twist_constraints()
            self.parent_to_heirachy()
        elif system == "skn":
            self.parent_to_heirachy()
        else:
            cmds.warning("Twist joint cannot be set on this system.")

    def ik_handle(self):
        cmds.select(clear=True)
        self.ik_hdl = cmds.ikHandle(n=f"hdl_{self.joint1_twist}", sj=self.joint1_twist, ee=self.joint2_twist, solver="ikSCsolver")[0]
        cmds.pointConstraint(self.joint2, f"hdl_{self.joint1_twist}")

    def correct_orientation(self):
        cmds.orientConstraint(self.joint1, self.joint2_twist)

    def twist_constraints(self):
        if len(self.tween_joints) > 3:
            cmds.error("self.tween_joints var cannot be greater than 3")
        else:
            for joint in self.tween_joints:
                cmds.orientConstraint([self.joint1_twist, self.joint2_twist], joint, n=f"orientConst_{joint}")
                cmds.pointConstraint([self.joint1_twist, self.joint2_twist], joint, n=f"pointConst_{joint}")

            if len(self.tween_joints) == 1:
                pass
            elif len(self.tween_joints) == 2:
                cmds.setAttr(f"orientConst_{self.tween_joints[0]}.{self.joint1_twist}W0",2)
                cmds.setAttr(f"pointConst_{self.tween_joints[0]}.{self.joint1_twist}W0",2)

                cmds.setAttr(f"orientConst_{self.tween_joints[1]}.{self.joint2_twist}W1",2)
                cmds.setAttr(f"pointConst_{self.tween_joints[1]}.{self.joint2_twist}W1",2)
            elif len(self.tween_joints) == 3:
                cmds.setAttr(f"orientConst_{self.tween_joints[0]}.{self.joint1_twist}W0",3)
                cmds.setAttr(f"pointConst_{self.tween_joints[0]}.{self.joint1_twist}W0",3)

                cmds.setAttr(f"orientConst_{self.tween_joints[2]}.{self.joint2_twist}W1",3)
                cmds.setAttr(f"pointConst_{self.tween_joints[2]}.{self.joint2_twist}W1",3)

        # checks if twist enabled if yes. point constraint to follow stretch
        if cmds.getAttr(f"{self.key['master_guide']}.{self.key['master_guide']}_squash_stretch", asString=1) == "Yes":
            cmds.pointConstraint(self.joint1, self.joint1_twist, n=f"pointConst_{self.joint1_twist}")
            cmds.pointConstraint(self.joint2, self.joint2_twist, n=f"pointConst_{self.joint2_twist}")

    def parent_to_heirachy(self):
        parent_joint = cmds.listRelatives(self.joint1, parent=True)
        if parent_joint is None:
            parent_joint = self.joint1
        cmds.parent(self.joint1_twist, parent_joint)
        if self.system == "rig":
            cmds.parent(self.ik_hdl, parent_joint)


def rig_to_skn(list):
    if list:
        for joint in list:
            cmds.parentConstraint(joint, f"jnt_skn{joint[7:]}", n=f"pConst_{joint}")
    else: pass
