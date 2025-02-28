import importlib
import maya.cmds as cmds

from mod.rig.utils import control_shape, OPM
importlib.reload(control_shape)

class create_hybrid():
    def __init__(self, ik_joint_list, fk_joint_list, master_guide, module):
        print(f"fk_joint_list: {fk_joint_list}")
        print(f"ik_joint_list: {ik_joint_list}")
        print(f"system: {module.system}")
        validation_joints = module.ik_joints
        system = module.system

        self.fk_ctrls = self.fk(ik_joint_list, fk_joint_list, system, master_guide, validation_joints)
        self.ik_ctrls = self.ik(ik_joint_list, validation_joints, master_guide)
        self.create_nodes(fk_joint_list, ik_joint_list, validation_joints, master_guide)

    def joint_prep(self):
        pass

    def ik(self, ik_joint_list, validation_joints, master_guide):
        ik_ctrls = []
        joint_skn_list = []
        other_joints = []
        for joint in ik_joint_list:
            if validation_joints["start_joint"] in joint:
                start_joint = joint
            elif validation_joints["end_joint"] in joint:
                end_joint = joint
            else:
                other_joints.append(joint)

        for joint in [start_joint, end_joint]:
            base_name = joint.replace("jnt_ik_","")
            control_module = control_shape.Controls(scale=1,ctrl_shape="cube",ctrl_name=f"ctrl_ik_{base_name}",rig_type="ik")
            ctrl_shape = control_module.return_ctrl()
            cmds.matchTransform(ctrl_shape, joint)
            ik_ctrls.append(ctrl_shape)

            cmds.select(ctrl_shape)
            joint = cmds.joint(n=f"jnt_crv_{base_name}")
            joint_skn_list.append(joint)
            cmds.select(clear=True)

        joint_positions = [cmds.xform(joint, q=True, t=True, ws=True) for joint in ik_joint_list]
        cv_curve = cmds.curve(d=3, p=joint_positions, n="mod_curve")
        ik_handle = cmds.ikHandle(solver="ikSplineSolver", startJoint=start_joint, endEffector=end_joint, curve=cv_curve, ccv=False, n=f"hdl_ik_{cmds.getAttr(f'{master_guide}.base_module',asString=True)}")
        skin_cluster = cmds.skinCluster(joint_skn_list, cv_curve, toSelectedBones=True)[0]
        
        OPM.offsetParentMatrix(ik_ctrls)

        return ik_ctrls

    def fk(self, ik_joint_list, fk_joint_list, system, master_guide, validation_joints):
        fk_ctrls = []
        for i, joint in enumerate(fk_joint_list):
            base_name = joint.replace("jnt_fk_","")
            grp_fk_offset = cmds.group(n=f"{base_name}_fk_offset", em=True, w=True)
            cmds.matchTransform(grp_fk_offset, joint)
            OPM.offsetParentMatrix(grp_fk_offset)
            grp_ik_orient = cmds.group(n=f"{base_name}_ik_orient", em=True, p=grp_fk_offset)
            grp_fk_orient = cmds.group(n=f"{base_name}_fk_orient", em=True, p=grp_ik_orient)

            cmds.pointConstraint(joint, grp_fk_offset, mo=True)
            cmds.orientConstraint(joint.replace("_fk_","_ik_"), grp_ik_orient, mo=True)

            control_module = control_shape.Controls(scale=1,guide=base_name,ctrl_name=f"ctrl_fk_{base_name}",rig_type="fk")
            ctrl_shape = control_module.return_ctrl()
            cmds.matchTransform(ctrl_shape, joint)
            cmds.parent(ctrl_shape, grp_fk_orient)
            fk_ctrls.append(ctrl_shape)

            cmds.orientConstraint(ctrl_shape, joint, mo=True)
            cmds.connectAttr(f"{joint.replace('_fk_','_ik_')}.translate",f"{joint}.translate")
        
        OPM.offsetParentMatrix(fk_ctrls)
        
        return fk_ctrls
    
    def create_nodes(self, fk_joint_list, ik_joint_list, validation_joints, master_guide):
        tmp_list = []
        for ctrl in self.fk_ctrls:
            pma_node = cmds.createNode("plusMinusAverage",n=f"{ctrl}_pma")
            tmp_list.append(ctrl)
            for i, x in enumerate(tmp_list):
                cmds.connectAttr(f"{x}.rotate",f"{pma_node}.input3D[{i}]")
            cmds.connectAttr(f"{pma_node}.output3D",f"{cmds.listRelatives(ctrl, p=True)[0]}.rotate")
        

        base_module = cmds.getAttr(f'{master_guide}.base_module',asString=True)
        db_node = cmds.createNode("distanceBetween",n=f"{base_module}_distanceBetween")
        cmds.connectAttr(f"{self.ik_ctrls[0]}.worldMatrix", f"{db_node}.inMatrix1")
        cmds.connectAttr(f"{self.ik_ctrls[-1]}.worldMatrix", f"{db_node}.inMatrix2")

        scale_factor = cmds.createNode("multiplyDivide", n=f"{base_module}_scale_factor")
        cmds.connectAttr(f"{db_node}.distance", f"{scale_factor}.input1X")
        cmds.setAttr(f"{scale_factor}.input2X", cmds.getAttr(f"{db_node}.distance"))
        cmds.setAttr(f"{scale_factor}.operation", 2)

        shape_presavation = cmds.createNode("multiplyDivide", n=f"{base_module}_shapePresavation")
        cmds.connectAttr(f"{scale_factor}.outputX",f"{shape_presavation}.input1X")
        cmds.setAttr(f"{shape_presavation}.operation", 3)
        cmds.setAttr(f"{shape_presavation}.input2X", -1)

        for joint in fk_joint_list:
            cmds.connectAttr(f"{scale_factor}.outputX", f"{joint}.scaleX")
            cmds.connectAttr(f"{shape_presavation}.outputX", f"{joint}.scaleY")
            cmds.connectAttr(f"{shape_presavation}.outputX",f"{joint}.scaleZ")

        for joint in ik_joint_list:
            cmds.connectAttr(f"{scale_factor}.outputX", f"{joint}.scaleX")
            cmds.connectAttr(f"{shape_presavation}.outputX", f"{joint}.scaleY")
            cmds.connectAttr(f"{shape_presavation}.outputX",f"{joint}.scaleZ")

    def get_ctrls(self):
        return self.fk_ctrls, self.ik_ctrls
