import maya.cmds as cmds
from systems.utils import OPM


class create_fk():
    def __init__(self, joint_list,master_guide,scale,delete_end):
        self.scale = scale
        self.fk_system(joint_list,delete_end)
        try:
            cmds.group(self.ctrls_fk[-1], n=f"grp_fk_ctrls_{master_guide}",w=1)
            cmds.group(joint_list[0],n=f"grp_fk_jnts_{master_guide}",w=1)
        except IndexError:
            pass

    def fk_system(self, fk_joint_list,delete_end):
        # delete_end = False
        self.ctrls_fk = []
        jnt_ctrls_fk = []
        fk_joint_list.reverse()
        scale = 10 * self.scale
        for i in range(len(fk_joint_list)):
            cmds.circle(n=f"ctrl_fk_{fk_joint_list[i][7:]}",
                        r=scale, nr=(1, 0, 0))
            cmds.matchTransform(f"ctrl_fk_{fk_joint_list[i][7:]}",
                                fk_joint_list[i])
            if delete_end is True:
                if cmds.listRelatives(fk_joint_list[i], c=True) is None:
                    cmds.delete(f"ctrl_fk_{fk_joint_list[i][7:]}")
            elif "root" in fk_joint_list[i]:
                cmds.delete(f"ctrl_fk_{fk_joint_list[i][7:]}")
            else:
                self.ctrls_fk.append(f"ctrl_fk_{fk_joint_list[i][7:]}")
                jnt_ctrls_fk.append(fk_joint_list[i])

        for ctrl in range(len(self.ctrls_fk)):
            try:
                cmds.parent(self.ctrls_fk[ctrl], self.ctrls_fk[ctrl+1])
            except IndexError:
                pass

        for ctrl in self.ctrls_fk:
            OPM.offsetParentMatrix(ctrl)

        self.fk_system_to_joint(jnt_ctrls_fk)
        fk_joint_list.reverse()  # debug

    def fk_system_to_joint(self, jnt_ctrls_fk):
        for item in range(len(self.ctrls_fk)):
            cmds.parentConstraint(self.ctrls_fk[item],
                                  jnt_ctrls_fk[item],
                                  n=f"pConst_{self.ctrls_fk[item]}")

    def get_ctrls(self):
        return self.ctrls_fk
