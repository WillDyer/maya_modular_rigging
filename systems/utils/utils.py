import maya.cmds as cmds

def create_ctrl(joint):
    ctrl_crv = cmds.circle(n=f"ctrl_ik_{joint[7:]}",r=1, nr=(1, 0, 0))
    cmds.matchTransform(ctrl_crv,joint)
    cmds.parentConstraint(ctrl_crv, joint,mo=1,n=f"pConst_{joint[7:]}")
    return f"ctrl_ik_{joint[7:]}"

def create_cube(name, scale):
    ctrlCV = cmds.curve(n=name,d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                    (0,1,0),(1,1,0),(1,0,0),(1,1,0),
                                    (1,1,1),(1,0,1),(1,1,1),
                                    (0,1,1),(0,0,1),(0,1,1),(0,1,0)])
                
    cmds.CenterPivot()
    cmds.xform(ctrlCV,t=(-.5,-.5,-.5))
    cmds.xform(ctrlCV,s=[scale[0],scale[1],scale[2]])
    cmds.select(ctrlCV)
    cmds.FreezeTransformations()
    cmds.delete(ctrlCV, ch=1) 
    return ctrlCV

def connector(first_jnt, second_jnt):
    first_point_loc = cmds.xform(first_jnt,q=1,ws=1,rp=1)
    second_point_loc = cmds.xform(second_jnt,q=1,ws=1,rp=1)
    cmds.curve( d=1, p=[first_point_loc, second_point_loc], n="connector_curve_" + first_jnt)
    cluster_1 = cmds.cluster(f"connector_curve_{first_jnt}.cv[0]", n="cluster_" + first_jnt + "_cv0")
    cluster_2 = cmds.cluster(f"connector_curve_{first_jnt}.cv[1]", n="cluster_" + second_jnt + "_cv1")
    cmds.parent(cluster_1[1], first_jnt)
    cmds.parent(cluster_2[1], second_jnt)
    for x in cmds.ls(typ="cluster"):
        cmds.hide(x+"Handle")
    cmds.setAttr(f"connector_curve_{first_jnt}.template", 1)

    curve = f"connector_curve_{first_jnt}"
    return curve

def constraint_from_lists_1to1(list_1, list_2, maintain_offset):
    for x in range(len(list_1)):
        if "root" in list_2[x]:
            pass
        else:
            cmds.parentConstraint(list_1[x], list_2[x],mo=maintain_offset, n=f"pConst_{list_1[x]}")

def constraint_from_lists_2to1(list_1, list_2, base_list, maintain_offset):
    for x in range(len(list_1)):
        if "root" in list_2[x]:
            pass
        else:
            cmds.parentConstraint(list_1[x], list_2[x], base_list[x], mo=maintain_offset, n=f"pConst_{list_1[x]}")

def colour_controls(ctrl_list):
    COLOR_CONFIG = {'l': 6, 'r': 13, 'default': 22}
    for ctrl in ctrl_list:
        try:
            cmds.setAttr(f"{ctrl}.overrideEnabled", 1)
            if ctrl == "ctrl_root":
                cmds.setAttr(f"{ctrl}.overrideColor", 14)
            elif ctrl[:4] == "ctrl":
                side = ctrl.split("_")[-2]
                try:
                    cmds.setAttr(f"{ctrl}.overrideColor",
                                COLOR_CONFIG[side])
                except KeyError:
                    cmds.setAttr(f"{ctrl}.overrideColor",
                                COLOR_CONFIG['default'])
                    pass
            else:
                pass
        except:
            pass