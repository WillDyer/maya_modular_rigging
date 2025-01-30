from importlib import reload
from maya import cmds, OpenMaya
import math

from mod.rig.utils import utils, control_shape
reload(utils)
reload(control_shape)


def create_pv(top_joint, pv_joint, end_joint, name="", pv_guide=""):
    start = cmds.xform(top_joint, q=1,ws=1,t=1)
    mid = cmds.xform(pv_joint, q=1,ws=1,t=1)
    end = cmds.xform(end_joint, q=1,ws=1,t=1)

    startV = OpenMaya.MVector(start[0], start[1], start[2])
    midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
    endV = OpenMaya.MVector(end[0], end[1], end[2])

    startEnd = endV - startV
    startMid = midV - startV

    dotP = startMid * startEnd

    proj = float(dotP) / float(startEnd.length())

    startEndN = startEnd.normal()

    projV = startEndN * proj
    arrowV = startMid - projV
    finalV = arrowV + midV

    cross1 = startEnd ^ startMid
    cross1.normalize()

    cross2 = cross1 ^ arrowV
    cross2.normalize()
    arrowV.normalize()

    matrixV = [arrowV.x, arrowV.y, arrowV.z, 0,
               cross1.x, cross1.y, cross1.z, 0,
               cross2.x, cross2.y, cross2.z, 0,
               0,0,0,1]

    matrixM = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList(matrixV, matrixM)

    matrixFn = OpenMaya.MTransformationMatrix(matrixM)

    rot = matrixFn.eulerRotation()

    control_module = control_shape.Controls(scale=[0.5,0.5,0.5],ctrl_name=name, ctrl_shape="cube", associated_guide=pv_guide)
    ctrl_crv = control_module.return_ctrl()
    cmds.xform(ctrl_crv, ws=1,t=(finalV.x, finalV.y, finalV.z))
    cmds.xform(ctrl_crv, ws=1, rotation=((rot.x/math.pi*180.0),
                                    (rot.y/math.pi*180.0),
                                    (rot.z/math.pi*180.0)))
    
    # extend distance if needed
    distance = utils.calculate_distance(obj1=ctrl_crv, obj2=pv_joint)
    if distance < 50:
        difference = 50 - distance
        cmds.xform(ctrl_crv, translation=(difference,0,0), r=True, os=True)

    curve = utils.connector(first_jnt=pv_joint, second_jnt=ctrl_crv)
    cmds.connectAttr(f"{ctrl_crv}.visibility",f"{curve}.visibility")
    if cmds.ls("tmp_world_space"):
        cmds.parent(curve, "tmp_world_space")
    else:
        cmds.group(curve, n="tmp_world_space", w=1)

    return ctrl_crv
