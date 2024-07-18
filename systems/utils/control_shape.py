import maya.cmds as cmds

def control_shape_list():
    return ["circle","cube","locator"]

class control_types():
    def __init__(self, name, scale):
        self.name = name
        self.scale = scale

    def create_circle(self):
        self.ctrl_crv = cmds.circle(n=self.name,r=1, nr=(1, 0, 0))
        return self.ctrl_crv
    
    def create_cube(self):
        self.ctrlCV = cmds.curve(n=self.name,d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                        (0,1,0),(1,1,0),(1,0,0),(1,1,0),
                                        (1,1,1),(1,0,1),(1,1,1),
                                        (0,1,1),(0,0,1),(0,1,1),(0,1,0)])
                    
        cmds.CenterPivot()
        cmds.xform(self.ctrlCV,t=(-.5,-.5,-.5))
        cmds.xform(self.ctrlCV,s=[self.scale[0],self.scale[1],self.scale[2]])
        cmds.select(self.ctrlCV)
        cmds.FreezeTransformations()
        cmds.delete(self.ctrlCV, ch=1) 
        return self.ctrlCV
    
    def create_locator(self):
        self.ctrl_crv = cmds.spaceLocator(n=self.name)
        return self.ctrl_crv

class controls():
    def __init__(self):
        pass

    def get_bounding_region(self):
        pass

    def set_control_size(self):
        pass

    def set_name(self):
        pass

    def return_ctrl(self):
        return self.ctrl