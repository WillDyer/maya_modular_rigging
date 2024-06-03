from maya import cmds, OpenMaya
import math

def create_pv(top_joint, pv_joint, end_joint): # can pass pv variable to pass existing curve
    # sel = cmds.ls(sl=1)
    
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
    
    cross1= startEnd ^ startMid
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
    
    
    loc = cmds.spaceLocator() # pv
    cmds.xform(loc, ws=1,t=(finalV.x, finalV.y, finalV.z))
    cmds.xform(loc, ws=1, rotation = ((rot.x/math.pi*180.0),
                                      (rot.y/math.pi*180.0),
                                      (rot.z/math.pi*180.0)))
    
    return loc

    
# get_pole_vector_position()
