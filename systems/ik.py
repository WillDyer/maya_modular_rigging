import maya.cmds as cmds
import importlib
from systems.utils import (OPM, cube_crv, pole_vector)

importlib.reload(OPM)
importlib.reload(pole_vector)
importlib.reload(cube_crv)

class create_ik():
    def __init__(self, ik_joint_list,master_guide,validation_joints):
        self.validation_joints = validation_joints
        self.ik_system(ik_joint_list)
        cmds.group(self.ik_ctrls,n=f"grp_ik_ctrls_{master_guide}",w=1)
        cmds.group(ik_joint_list[0],n=f"grp_ik_jnts_{master_guide}",w=1)

    def ik_system(self, ik_joint_list):
        #print(self.validation_joints)
        for joint in ik_joint_list:
            if self.validation_joints["start_joint"] in joint:
                self.start_joint = joint
            elif self.validation_joints["pv_joint"] in joint:
                self.pv_joint = joint
            elif self.validation_joints["end_joint"] in joint:
                self.end_joint = joint
            else:
                # Could use this to generate list for eg. shoulder ctrls
                pass
        pv_ctrl = self.create_pv()
        hdl_ctrl = self.create_handle()
        root_ctrl = self.create_top_hdl_ctrl()
        self.ik_ctrls = [pv_ctrl,hdl_ctrl,root_ctrl]

    def create_pv(self):
        pv_ctrl = pole_vector.create_pv(self.start_joint, self.pv_joint, self.end_joint)
        cmds.rename(pv_ctrl, f"ctrl_pv_{self.pv_joint[7:]}")
        return f"ctrl_pv_{self.pv_joint[7:]}"

    def create_handle(self):
        ctrl_crv = cube_crv.create_cube(f"ctrl_ik_{self.end_joint[7:]}",scale=[5,5,5])
        cmds.ikHandle(n=f"hdl_ik_{self.end_joint[7:]}", solver="ikRPsolver", sj=self.start_joint, ee=self.end_joint)
        cmds.poleVectorConstraint(f"ctrl_pv_{self.pv_joint[7:]}", f"hdl_ik_{self.end_joint[7:]}", n=f"pvConst_{self.pv_joint[7:]}")
        if self.validation_joints["world_orientation"] == True:
            cmds.matchTransform(ctrl_crv, f"hdl_ik_{self.end_joint[7:]}")
        else:
            cmds.matchTransform(ctrl_crv, self.end_joint)
        cmds.parentConstraint(ctrl_crv, f"hdl_ik_{self.end_joint[7:]}",mo=1,n=f"pConst_hdl_ik_{self.end_joint[7:]}")
        OPM.offsetParentMatrix(ctrl_crv)
        return ctrl_crv

    def create_top_hdl_ctrl(self):
        ctrl_crv = cmds.circle(n=f"ctrl_ik_{self.start_joint[7:]}",r=10, nr=(1, 0, 0))
        cmds.matchTransform(ctrl_crv,self.start_joint)
        cmds.parentConstraint(ctrl_crv, self.start_joint,mo=1,n=f"pConst_{self.start_joint[7:]}")
        return ctrl_crv[0]
    
    def get_ctrls(self):
        return self.ik_ctrls
