import maya.cmds as cmds

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
    #cmds.rename("ctrl_", ignoreShape=1)
    cmds.delete(ctrlCV, ch=1)
    
    return ctrlCV