import maya.cmds as cmds
from systems.utils import OPM

class create_fk():
    def __init__(self, joint_list,delete_end):
        self.fk_system(joint_list,delete_end)


    def fk_system(self, fk_joint_list,delete_end):
        #delete_end = False
        ctrls_fk = []
        jnt_ctrls_fk = []
        fk_joint_list.reverse()
        for i in range(len(fk_joint_list)):
            cmds.circle(n=f"ctrl_fk_{fk_joint_list[i][7:]}",
                        r=10, nr=(1, 0, 0))
            cmds.matchTransform(f"ctrl_fk_{fk_joint_list[i][7:]}",
                                fk_joint_list[i])
            if delete_end == True:
                if cmds.listRelatives(fk_joint_list[i], c=True) is None:
                    cmds.delete(f"ctrl_fk_{fk_joint_list[i][7:]}")
            elif "root" in fk_joint_list[i]:
                cmds.delete(f"ctrl_fk_{fk_joint_list[i][7:]}")
            else:
                ctrls_fk.append(f"ctrl_fk_{fk_joint_list[i][7:]}")
                jnt_ctrls_fk.append(fk_joint_list[i])

        for ctrl in range(len(ctrls_fk)):
            try:
                cmds.parent(ctrls_fk[ctrl], ctrls_fk[ctrl+1])
            except IndexError:
                pass

        for ctrl in ctrls_fk:
            OPM.offsetParentMatrix(ctrl)

        self.fk_system_to_joint(ctrls_fk, jnt_ctrls_fk)
        fk_joint_list.reverse() #debug

    def fk_system_to_joint(self, ctrls_fk, jnt_ctrls_fk):
        for item in range(len(ctrls_fk)):
            cmds.parentConstraint(ctrls_fk[item],
                                  jnt_ctrls_fk[item],
                                  n=f"pConst_{ctrls_fk[item]}")
