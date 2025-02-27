import maya.cmds as cmds
from mod.rig.utils import OPM, control_shape
import importlib
importlib.reload(control_shape)


class create_fk():
    def __init__(self, joint_list,master_guide,scale,delete_end):
        self.scale = scale
        self.fk_system(joint_list,delete_end)
        try:
            cmds.group(self.offset, n=f"grp_fk_ctrls_{master_guide}",w=1)
            cmds.group(joint_list[0],n=f"grp_fk_jnts_{master_guide}",w=1)
        except IndexError:
            pass

    def fk_system(self, fk_joint_list,delete_end):
        # delete_end = False
        self.ctrls_fk = []
        jnt_ctrls_fk = []
        fk_joint_list.reverse()
        scale = self.scale

        if delete_end is True:
            loop_list = fk_joint_list
            loop_list.remove(fk_joint_list[0])
        else:
            loop_list = fk_joint_list

        for i in range(len(loop_list)):
            control_module = control_shape.Controls(scale,guide=loop_list[i][7:],ctrl_name=f"ctrl_fk_{loop_list[i][7:]}",rig_type="fk")
            ctrl_shape = control_module.return_ctrl()
            cmds.matchTransform(ctrl_shape, loop_list[i])

            self.ctrls_fk.append(ctrl_shape)
            jnt_ctrls_fk.append(loop_list[i])

            if "root" in loop_list[i]:
                cmds.delete(ctrl_shape)
                self.ctrls_fk.remove(ctrl_shape)
                jnt_ctrls_fk.remove(loop_list[i])

        for ctrl in range(len(self.ctrls_fk)):
            try:
                cmds.parent(self.ctrls_fk[ctrl], self.ctrls_fk[ctrl+1])
            except IndexError:
                pass

        for ctrl in self.ctrls_fk:
            OPM.offsetParentMatrix(ctrl)

        offset = self.ctrls_fk[-1].replace("ctrl_","offset_")
        self.offset = cmds.group(n=offset, em=True)
        cmds.matchTransform(self.offset, self.ctrls_fk[-1])
        cmds.parent(self.ctrls_fk[-1], self.offset)
        OPM.offsetParentMatrix(self.ctrls_fk[-1])

        self.fk_system_to_joint(jnt_ctrls_fk)
        fk_joint_list.reverse()  # debug

    def fk_system_to_joint(self, jnt_ctrls_fk):
        for item in range(len(self.ctrls_fk)):
            cmds.parentConstraint(self.ctrls_fk[item],
                                  jnt_ctrls_fk[item],
                                  n=f"pConst_{self.ctrls_fk[item]}")

    def get_ctrls(self):
        return self.ctrls_fk
