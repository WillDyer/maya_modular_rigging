import maya.cmds as cmds
import importlib
from systems.utils import (OPM, utils, pole_vector)

importlib.reload(OPM)
importlib.reload(pole_vector)
importlib.reload(utils)

# CLEAN THIS FILE UP

class create_ik():
    def __init__(self, ik_joint_list,master_guide,validation_joints):
        self.above_root_joints = []
        self.below_root_joints = []
        self.validation_joints = validation_joints
        self.ik_system(ik_joint_list)
        cmds.group(self.ik_ctrls,n=f"grp_ik_ctrls_{master_guide}",w=1)
        cmds.group(ik_joint_list[0],n=f"grp_ik_jnts_{master_guide}",w=1)

    def ik_system(self, ik_joint_list):
        self.other_joints = []
        for joint in ik_joint_list:
            if self.validation_joints["start_joint"] in joint:
                self.start_joint = joint
            elif self.validation_joints["pv_joint"] in joint:
                self.pv_joint = joint
            elif self.validation_joints["end_joint"] in joint:
                self.end_joint = joint
            else:
                self.other_joints.append(joint)
                pass

        self.collect_other_controls(ik_joint_list)
        pv_ctrl = self.create_pv()
        hdl_ctrl = self.create_handle()
        root_ctrl = self.create_top_hdl_ctrl()
        above_ctrls = self.above_root_ctrl()
        print(f"ABOVE CTRL {above_ctrls}")
        if above_ctrls:
            self.ik_ctrls = [pv_ctrl,hdl_ctrl,above_ctrls[-1], root_ctrl]
        else:
            self.ik_ctrls = [pv_ctrl,hdl_ctrl,root_ctrl]
        OPM.offsetParentMatrix(self.ik_ctrls)

    def create_pv(self):
        pv_ctrl = pole_vector.create_pv(self.start_joint, self.pv_joint, self.end_joint)
        cmds.rename(pv_ctrl, f"ctrl_pv_{self.pv_joint[7:]}")
        return f"ctrl_pv_{self.pv_joint[7:]}"

    def create_handle(self):
        ctrl_crv = utils.create_cube(f"ctrl_ik_{self.end_joint[7:]}",scale=[5,5,5])
        cmds.ikHandle(n=f"hdl_ik_{self.end_joint[7:]}", solver="ikRPsolver", sj=self.start_joint, ee=self.end_joint)
        cmds.poleVectorConstraint(f"ctrl_pv_{self.pv_joint[7:]}", f"hdl_ik_{self.end_joint[7:]}", n=f"pvConst_{self.pv_joint[7:]}")
        if self.validation_joints["world_orientation"] == True:
            cmds.matchTransform(ctrl_crv, f"hdl_ik_{self.end_joint[7:]}")
        else:
            cmds.matchTransform(ctrl_crv, self.end_joint)
        cmds.parentConstraint(ctrl_crv, f"hdl_ik_{self.end_joint[7:]}",mo=1,n=f"pConst_hdl_ik_{self.end_joint[7:]}")
        return ctrl_crv

    def create_top_hdl_ctrl(self):
        self.start_ctrl_crv = cmds.circle(n=f"ctrl_ik_{self.start_joint[7:]}",r=10, nr=(1, 0, 0))[0]
        cmds.matchTransform(self.start_ctrl_crv,self.start_joint)
        cmds.parentConstraint(self.start_ctrl_crv, self.start_joint,mo=1,n=f"pConst_{self.start_joint[7:]}")
        return self.start_ctrl_crv
    
    def get_ctrls(self):
        return self.ik_ctrls
    
    def collect_other_controls(self, ik_joint_list):
        start_index = ik_joint_list.index(self.start_joint)
        end_index = ik_joint_list.index(self.end_joint)
        for joint in self.other_joints:
            joint_index = ik_joint_list.index(joint)
            if joint_index < start_index:
                self.above_root_joints.append(joint)
            elif joint_index > end_index:
                self.below_root_joints.append(joint)

    def above_root_ctrl(self):
        above_root_control_list = []
        if self.above_root_joints:
            for joint in self.above_root_joints:
                ctrl_crv_tmp = cmds.circle(n=f"ctrl_ik_{joint[7:]}",r=10,nr=(1, 0, 0))[0]
                cmds.matchTransform(ctrl_crv_tmp,joint)
                cmds.parentConstraint(ctrl_crv_tmp, joint,mo=1,n=f"pConst_{joint[7:]}")
                above_root_control_list.append(ctrl_crv_tmp)
            cmds.parent(self.start_ctrl_crv,above_root_control_list[0])
        return above_root_control_list

