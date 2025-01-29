import maya.cmds as cmds
import importlib
from mod.rig.utils import OPM, utils

importlib.reload(OPM)
importlib.reload(utils)


class PrepSkeleton():
    def __init__(self,orientation,key,system):
        self.tweak_joint_dict = {}
        self.orientation = orientation
        self.key = key
        self.system = system
        self.module = importlib.import_module(f"mod.modules.{self.key['module']}")
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
                returned_values = self.insert_joints_between(num_joints)
                self.tween_joint_list = returned_values["tween_joint_list"]
                self.tweak_joint_list = returned_values["tweak_joint_list"]
                self.twist_joint_dict = {
                    "joint1": self.joint1,
                    "joint1_twist": self.joint1_twist,
                    "joint2": self.joint2,
                    "joint2_twist": self.joint2_twist,
                    "tween_joints": self.tween_joint_list,
                    "tweak_joints": self.tweak_joint_list
                }

                tmp_tweak_joint_dict = {
                    "master_guide": self.key["master_guide"],
                    "tween_joints": self.tween_joint_list,
                    "tweak_joints": self.tweak_joint_list,
                    "joint1_twist": self.joint1_twist,
                    "joint2_twist": self.joint2_twist
                }
                self.tweak_joint_dict[self.joint1] = tmp_tweak_joint_dict
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
        tweak_joint_list = []

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
        cmds.parent(self.joint2, self.joint1)

        for joint in tween_joint_list:
            cmds.parent(joint, w=True)

        # twist joint1 & joint2
        self.joint1_twist = f"{self.joint1}_twist"
        self.make_joint(joint_name=self.joint1_twist, locator=self.joint1)
        parent_joint = cmds.listRelatives(f"{self.joint1}_twist", parent=True)
        if parent_joint: cmds.parent(f"{self.joint1}_twist", w=True)
        joint2_split = self.joint2.split("_")
        joint2_split.insert(2, f"tween{num_joints + 1}")
        self.joint2_twist = '_'.join(joint2_split)
        self.make_joint(joint_name=self.joint2_twist, locator=self.joint2)
        cmds.parent(self.joint2_twist, w=True)
        # tween_joint_list.append(joint2_twist)

        # parenting
        for joint in tween_joint_list:
            cmds.parent(joint, self.joint1_twist)
        cmds.parent(self.joint2_twist, self.joint1_twist)

        # # tweak joints
        # for joint in tween_joint_list:
        #     tweak_joint_name = joint.replace("tween","tweak")
        #     cmds.select(joint)
        #     cmds.joint(n=tweak_joint_name,r=0.5)
        #     cmds.select(clear=1)
        #     tweak_joint_list.append(tweak_joint_name)

        return_dict = {
            "tween_joint_list": tween_joint_list,
            "tweak_joint_list": tweak_joint_list
        }
        return return_dict

    def return_data(self):
        return_data_dict = {
            "return_data_list": self.return_data_list,
            "tweak_joint_dict": self.tweak_joint_dict
        }

        return return_data_dict

    def make_joint(self, joint_name=None, locator=None):
        loc = cmds.xform(locator, q=True, ws=True, t=True)  # Gather worldspace location
        rot = cmds.xform(locator, q=True, ws=True, ro=True) # gather worldspace rotation
        jnt_name = cmds.joint(n=f"{joint_name}", p=loc)  # create joint based off the location
        cmds.xform(jnt_name, ws=True, ro=rot)
        cmds.makeIdentity(jnt_name, apply=True, t=False, r=True, s=False)


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
        self.tweak_joints = twist_joint_dict["tweak_joints"]

        self.module = importlib.import_module(f"mod.modules.{self.key['module']}")
        importlib.reload(self.module)
        
        self.offset = -10
        self.offset_locator = -10
        self.aim_axis = -1
        try:
            if cmds.getAttr(f"{self.key['master_guide']}.is_mirrored", asString=True) == "Yes":
                self.offset_locator = 10
                self.aim_axis = 1
        except KeyError:
            pass

        if system == "rig":
            if self.module.twist_joint["end"] in self.joint2: # treat end twist differently
                cmds.joint(self.joint2_twist, e=True, oj="none",ch=True, zso=True)
                self.correct_orientation(list=self.tween_joints, target=self.joint2)
                self.reverse_twist()
                self.tween_falloff(source_rot=self.joint2_twist)
                self.scale_integration()
                self.parent_to_heirachy(parent_type="specific", joint=self.joint1)
            else:
                cmds.joint(self.joint2_twist, e=True, oj="none",ch=True, zso=True)
                root_orient, end_orient, aim_loc = self.create_orientation()
                self.stable_orientation(top_twist=root_orient, end_twist=end_orient, loc=aim_loc)
                self.tween_falloff(source_rot=self.joint1)
                self.parent_to_heirachy(parent_type="parent")
                self.scale_integration()
                cmds.group(root_orient, n=f"grp_twist_jnts_{self.key['master_guide']}", w=1)
        elif system == "skn":
            self.parent_to_heirachy()
        else:
            cmds.warning("twist_joints: Twist joint cannot be set on this system.")

    def ik_handle(self, start_joint="", end_joint=""):
        cmds.select(clear=True)
        ik_hdl = cmds.ikHandle(n=f"hdl_{start_joint}", sj=start_joint, ee=end_joint, solver="ikRPsolver")[0]
        return ik_hdl

    def correct_orientation(self, list=[], target=""):
        for item in list:
            aim_const = cmds.aimConstraint(target, item, u=[1,0,0])
            cmds.delete(aim_const)
            cmds.makeIdentity(item, apply=True, t=False, r=True, s=False)

    def create_orientation(self):
        duplicate_list = []
        orient_suffix = "orient"

        self.correct_orientation(list=self.tween_joints, target=self.joint2)
        
        root_orient = cmds.duplicate(self.joint1_twist, n=f"{self.joint1_twist}_{orient_suffix}", po=True)[0]
        for joint in self.tween_joints:
            dupe = cmds.duplicate(joint, n=f"{joint}_{orient_suffix}", po=True)[0]
            cmds.parent(dupe, w=True)
            duplicate_list.append(dupe)
        
        cmds.parent(duplicate_list, root_orient)
        
        cmds.xform(root_orient, translation=(0,0,self.offset), r=True)
        aim_loc = cmds.spaceLocator(n=f"{self.joint1_twist.replace('jnt_rig','loc')}_aim")[0]
        cmds.matchTransform(aim_loc, root_orient)
        cmds.parent(aim_loc, root_orient)
        cmds.xform(aim_loc, translation=(0,0,self.offset_locator), r=True)
        
        cmds.hide(root_orient)
        cmds.select(clear=True)
        return root_orient, duplicate_list[-1], aim_loc

    def stable_orientation(self, top_twist="", end_twist="", loc=""):
        cmds.aimConstraint(self.joint2, self.joint1_twist, u=[0,0,self.aim_axis], wut="object", wuo=loc, mo=True)

        handle = self.ik_handle(start_joint=top_twist, end_joint=end_twist)
        cmds.parent(handle, self.joint2)
        cmds.matchTransform(handle, self.joint2)
        cmds.hide(handle)

        for XYZ in ["X","Y","Z"]:
            cmds.setAttr(f"{handle}.poleVector{XYZ}",0)

        connect_to = self.key["system_to_connect"]
        if connect_to:
            cmds.parentConstraint(f"jnt_rig_{connect_to[1]}", top_twist, mo=True, n=f"pConst_{top_twist.replace('jnt_rig_','')}")
        else:
            cmds.parentConstraint(self.key["joints"][0], top_twist, mo=True, n=f"pConst_{top_twist.replace('jnt_rig_','')}")

    def tween_falloff(self, source_rot=""):
        def get_middle_values(length=0):
            if length <= 0:
                return []
            return [round(i / (length + 1), 2) for i in range(1, length + 1)]
            
        multi_node = cmds.createNode('multiplyDivide', name=f'multi_{source_rot}_twist')
        clean_name = source_rot.replace("jnt_rig_tween3_", "").replace("jnt_rig_", "")
        user_multi_node = cmds.createNode('multiplyDivide', name=f"user_twist_{clean_name}")
        
        XYZ = ["X","Y","Z"]
        if len(self.tween_joints) <= 3:
            values = get_middle_values(length=len(self.tween_joints))
        else:
            values = []

        for i, joint in enumerate(self.tween_joints):
            try:
                cmds.connectAttr(f"{source_rot}.rotateX", f"{multi_node}.input1{XYZ[i]}")
                cmds.connectAttr(f"{multi_node}.output{XYZ[i]}", f"{user_multi_node}.input1{XYZ[i]}")
                cmds.connectAttr(f"{user_multi_node}.output{XYZ[i]}", f"{joint}.rotateX")
                cmds.setAttr(f"{multi_node}.input2{XYZ[i]}", values[i])
            except Exception:
                pass

    def reverse_twist(self):
        aim_loc = cmds.spaceLocator(n=f"{self.joint2_twist.replace('jnt_rig_','')}_aim")[0]
        cmds.matchTransform(aim_loc, self.joint2_twist)
        cmds.parent(aim_loc, self.joint2)
        cmds.xform(aim_loc, translation=(0,0,self.offset_locator), r=True)

        cmds.aimConstraint(self.joint1, self.joint2_twist, u=[0,0,self.aim_axis], wut="object", wuo=aim_loc, mo=True)
        cmds.hide(aim_loc)

    def parent_to_heirachy(self, parent_type="", joint=""):
        if parent_type == "parent":
            parent_joint = cmds.listRelatives(self.joint1, parent=True)[0]
            if parent_joint is None:
                parent_joint = self.joint1
            cmds.connectAttr(f"{self.joint1}.translate",f"{self.joint1_twist}.translate")
            cmds.parent(self.joint1_twist, parent_joint)
        elif parent_type == "specific":
            cmds.parent(self.joint1_twist, joint)

    def scale_integration(self):
        cmds.connectAttr(f"{self.joint2}.translateX",f"{self.joint2_twist}.translateX")

        for tween in self.tween_joints:
            cmds.pointConstraint(self.joint1, self.joint2_twist, tween, n=f"pointConst_{tween}",mo=False)
        
        if len(self.tween_joints) == 1:
            pass
        elif len(self.tween_joints) == 2:
            cmds.setAttr(f"pointConst_{self.tween_joints[0]}.{self.joint1}W0",2)
            cmds.setAttr(f"pointConst_{self.tween_joints[1]}.{self.joint2_twist}W1",2)
        elif len(self.tween_joints) == 3:
            cmds.setAttr(f"pointConst_{self.tweak_joints[0]}.{self.joint1}W0",3)
            cmds.setAttr(f"pointConst_{self.tweak_joints[2]}.{self.joint2_twist}W1",3)


def connect_user_twist():
    multi_nodes = cmds.ls("user_twist*", type="multiplyDivide")

    for multi in multi_nodes:
        input1_connections = [
            attr for attr in ["input1X", "input1Y", "input1Z"]
            if cmds.listConnections(f"{multi}.{attr}", source=True)
        ]
        
        guide = multi.replace("user_twist_", "")

        for i, input1 in enumerate(input1_connections):
            input2 = input1.replace("1", "2")            
            if cmds.listConnections(f"{multi}.{input2}", source=True, plugs=True): # makes proxy
                for ctrl_type in ["ik", "fk"]:
                    ctrl = f"ctrl_{ctrl_type}_{guide}"
                    if cmds.objExists(ctrl):
                        attr = f"twist_multi_{guide}_{i}_proxy"
                        if not cmds.attributeQuery(attr, node=ctrl, exists=True):
                            cmds.addAttr(ctrl, sn=attr, nn=f"Proxy Twist Multi {i}", at="float", k=True, dv=1)
                        cmds.connectAttr(f"{ctrl}.{attr}", f"{multi}.{input2}", force=True)
                        break
            else:
                for ctrl_type in ["ik", "fk"]:
                    ctrl = f"ctrl_{ctrl_type}_{guide}"
                    if cmds.objExists(ctrl):
                        attr = f"twist_multi_{guide}_{i}"
                        if not cmds.attributeQuery(attr, node=ctrl, exists=True):
                            cmds.addAttr(ctrl, sn=attr, nn=f"Twist Multi {i}", at="float", k=True, dv=1)
                        cmds.connectAttr(f"{ctrl}.{attr}", f"{multi}.{input2}", force=True)
                        break
