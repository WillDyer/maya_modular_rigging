import maya.cmds as cmds
import maya.mel as mel
import importlib
from systems.utils import (OPM, utils, pole_vector,control_shape)

importlib.reload(OPM)
importlib.reload(pole_vector)
importlib.reload(utils)
importlib.reload(control_shape)

# CLEAN THIS FILE UP


class create_ik():
    def __init__(self, ik_joint_list,master_guide,validation_joints):
        mel.eval("ikSpringSolver;")
        self.above_root_joints = []
        self.below_root_joints = []
        self.validation_joints = validation_joints
        self.ik_system(ik_joint_list)

        cmds.group(self.grouped_ctrls,n=f"grp_ik_ctrls_{master_guide}",w=1)
        cmds.group(ik_joint_list[0],n=f"grp_ik_jnts_{master_guide}",w=1)
        if self.validation_joints["ik_type"] == "quadruped":
            cmds.parent(self.driver_joint_list[-1], f"grp_ik_jnts_{master_guide}")

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

        if self.validation_joints["ik_type"] == "biped":
            self.collect_other_controls(ik_joint_list)
            pv_ctrl = self.create_pv()
            hdl_ctrl = self.create_handle(self.start_joint, self.end_joint, solver="ikRPsolver", pv=True, constrain=True)
            root_ctrl = self.create_top_hdl_ctrl()
            above_ctrls = self.above_root_ctrl()

        elif self.validation_joints["ik_type"] == "quadruped":
            self.driver_joint_list = []
            hock_joint = [joint for joint in ik_joint_list if self.validation_joints["hock"] in joint][0]
            self.collect_other_controls(ik_joint_list)
            pv_ctrl = self.create_pv()

            for joint in ik_joint_list:
                driver_joint = cmds.duplicate(joint, n=f"{joint}_driver", parentOnly=True)[0]
                try: cmds.parent(driver_joint, w=True)  # catches obj if parented to world already
                except: pass
                self.driver_joint_list.append(driver_joint)

            self.driver_joint_list.reverse()
            for joint in range(len(self.driver_joint_list)):
                try: cmds.parent(self.driver_joint_list[joint], self.driver_joint_list[joint+1])
                except IndexError: pass

            root_ctrl = self.create_top_hdl_ctrl()
            hock_ctrl = self.create_handle(self.start_joint, hock_joint, solver="ikRPsolver", pv=True, constrain=False)
            single_chain = cmds.ikHandle(sj=hock_joint, ee=self.end_joint, solver="ikSCsolver", n=f"ik_hdl_sc_{self.end_joint}")[0]

            hdl_ctrl = self.create_handle(f"{self.start_joint}_driver", f"{self.end_joint}_driver", solver="ikSpringSolver", pv=False, constrain=True)
            # cmds.parent(hock_ctrl, hdl_ctrl)
            
            hock_grp = cmds.group(n=f"offset_{hock_ctrl}", em=True)
            cmds.matchTransform(hock_grp, hdl_ctrl)
            cmds.parent(hock_ctrl, hock_grp)
            cmds.parentConstraint(hdl_ctrl, hock_grp, mo=True, sr=["x","y","z"]) 

            loc = cmds.xform(hdl_ctrl, r=True, ws=True, q=True, t=True)
            cmds.xform(hock_ctrl, pivots=loc, ws=True)

            grp = cmds.group(n=f"hdl_ik_{hock_joint[7:]}_offset", em=1, p=f"{hock_joint}_driver")
            cmds.matchTransform(grp, hdl_ctrl)
            cmds.parent(f"hdl_ik_{hock_joint[7:]}", grp)
            cmds.parentConstraint(hock_ctrl, grp, mo=1, n=f"pConst_{hock_ctrl}")

            cmds.parent(single_chain, f"{self.end_joint}_driver")
            cmds.parentConstraint(root_ctrl, self.driver_joint_list[-1], mo=1, n=f"pConst_{self.driver_joint_list[-1]}")
            OPM.offsetParentMatrix(hock_ctrl)
            above_ctrls = self.above_root_ctrl()
            cmds.setAttr(f"{hock_ctrl}.translate", lock=True)
            for xyz in ["X","Y","Z"]: cmds.setAttr(f"{hock_ctrl}.translate{xyz}", keyable=False, cb=False)
            cmds.hide(self.driver_joint_list[-1])
        else:
            cmds.error("ik_type is invalid. Ik rig not made")

        if above_ctrls:
            if hock_grp: self.ik_ctrls = [pv_ctrl, hdl_ctrl, hock_grp, root_ctrl] + above_ctrls
            else: self.ik_ctrls = [pv_ctrl,hdl_ctrl,root_ctrl] + above_ctrls
            # self.grouped_ctrls = [pv_ctrl, hdl_ctrl, above_ctrls[0]]
            offset = self.ik_ctrls[-1].replace("ctrl_","offset_")
        else:
            if hock_grp: self.ik_ctrls = [pv_ctrl,hdl_ctrl,hock_grp,root_ctrl]
            else: self.ik_ctrls = [pv_ctrl,hdl_ctrl,root_ctrl]
            # self.grouped_ctrls = [pv_ctrl,hdl_ctrl,root_ctrl]
            offset = self.ik_ctrls[-1].replace("ctrl_","offset_")

        self.offset = cmds.group(n=offset, em=1)
        cmds.matchTransform(self.offset, self.ik_ctrls[-1])
        cmds.parent(self.ik_ctrls[-1], self.offset)
        if hock_grp: self.grouped_ctrls = [pv_ctrl, hdl_ctrl, hock_grp, self.offset]
        else: self.grouped_ctrls = [pv_ctrl,hdl_ctrl,self.offset]
        OPM.offsetParentMatrix(self.ik_ctrls)

    def create_pv(self):
        pv_ctrl = pole_vector.create_pv(self.start_joint, self.pv_joint, self.end_joint)
        cmds.rename(pv_ctrl, f"ctrl_pv_{self.pv_joint[7:]}")
        return f"ctrl_pv_{self.pv_joint[7:]}"

    def create_handle(self, start_joint, end_joint, solver, pv, constrain):
        control_module = control_shape.Controls(scale=[1,1,1],guide=self.end_joint[7:],ctrl_name=f"ctrl_ik_{end_joint[7:]}",rig_type="ik")
        ctrl_crv = control_module.return_ctrl()
        self.handle = cmds.ikHandle(n=f"hdl_ik_{end_joint[7:]}", solver=solver, sj=start_joint, ee=end_joint)
        if pv: cmds.poleVectorConstraint(f"ctrl_pv_{self.pv_joint[7:]}", f"hdl_ik_{end_joint[7:]}", n=f"pvConst_{self.pv_joint[7:]}")
        if self.validation_joints["world_orientation"] is True:
            cmds.matchTransform(ctrl_crv, f"hdl_ik_{end_joint[7:]}")
        else:
            cmds.matchTransform(ctrl_crv, end_joint)
        if constrain:
            cmds.parentConstraint(ctrl_crv, f"hdl_ik_{end_joint[7:]}",mo=1,n=f"pConst_hdl_ik_{end_joint[7:]}")
        cmds.addAttr(ctrl_crv, ln="handle",at="enum",en="True",k=0)
        return ctrl_crv

    def create_top_hdl_ctrl(self):
        cmds.select(clear=1)
        control_module = control_shape.Controls(scale=1,guide=self.start_joint[7:],ctrl_name=f"ctrl_ik_{self.start_joint[7:]}",rig_type="ik")
        self.start_ctrl_crv = control_module.return_ctrl()
        cmds.matchTransform(self.start_ctrl_crv,self.start_joint)
        cmds.parentConstraint(self.start_ctrl_crv, self.start_joint,mo=1,n=f"pConst_{self.start_joint[7:]}")
        return self.start_ctrl_crv

    def get_ctrls(self):
        return self.ik_ctrls

    def get_ik_hdl(self):
        return self.handle

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
        self.to_be_parented = []
        if self.above_root_joints:
            for joint in self.above_root_joints:
                control_module = control_shape.Controls(scale=1,guide=joint[7:],ctrl_name=f"ctrl_ik_{joint[7:]}",rig_type="ik")
                ctrl_crv_tmp = control_module.return_ctrl()
                self.to_be_parented.append(ctrl_crv_tmp)
                cmds.matchTransform(ctrl_crv_tmp,joint)
                cmds.parentConstraint(ctrl_crv_tmp, joint,mo=1,n=f"pConst_{joint[7:]}")
            cmds.parent(self.start_ctrl_crv,self.to_be_parented[0])
            for ctrl in range(len(self.to_be_parented)):
                if ctrl == 0:
                    pass
                else:
                    try: cmds.parent(self.to_be_parented[ctrl],self.to_be_parented[ctrl+1])
                    except: pass
        return self.to_be_parented
