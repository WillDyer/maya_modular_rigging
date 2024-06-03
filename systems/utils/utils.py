import maya.cmds as cmds

def create_ctrl(joint):
    ctrl_crv = cmds.circle(n=f"ctrl_ik_{joint[7:]}",r=1, nr=(1, 0, 0))
    cmds.matchTransform(ctrl_crv,joint)
    cmds.parentConstraint(ctrl_crv, joint,mo=1,n=f"pConst_{joint[7:]}")
    return f"ctrl_ik_{joint[7:]}"

def create_cube():
    ctrlCV = cmds.curve(n="ctrl_cube_#",d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                    (0,1,0),(1,1,0),(1,0,0),(1,1,0),
                                    (1,1,1),(1,0,1),(1,1,1),
                                    (0,1,1),(0,0,1),(0,1,1),(0,1,0)])
                
    cmds.CenterPivot()
    cmds.xform(ctrlCV,t=(-.5,-.5,-.5))
    cmds.select(ctrlCV)
    cmds.FreezeTransformations()
    cmds.delete(ctrlCV, ch=1)
    
    return ctrlCV

def connector(first_jnt, second_jnt):
    pv_joint_loc = cmds.xform(first_jnt,q=1,ws=1,rp=1)
    ctrl_pv_loc = cmds.xform(second_jnt,q=1,ws=1,rp=1)
    cmds.curve( d=1, p=[pv_joint_loc, ctrl_pv_loc], n="connector_curve_" + first_jnt)
    cluster_1 = cmds.cluster(f"connector_curve_{first_jnt}.cv[0]", n="cluster_" + first_jnt + "_cv0")
    cluster_2 = cmds.cluster(f"connector_curve_{first_jnt}.cv[1]", n="cluster_" + second_jnt + "_cv1")
    cmds.parent(cluster_1[1], first_jnt)
    cmds.parent(cluster_2[1], second_jnt)
    for x in cmds.ls(typ="cluster"):
        cmds.hide(x+"Handle")
    cmds.setAttr(f"connector_curve_{first_jnt}.template", 1)

    cluster_list = f"connector_curve_{first_jnt}"
    return cluster_list

def constraint_from_lists(list_1, list_2, maintain_offset):
    list_2.reverse()
    for x in range(len(list_1)):
        if "root" in list_2[x]:
            pass
        else:
            cmds.parentConstraint(list_1[x], list_2[x],mo=maintain_offset, n=f"pConst_{list_1[x]}")