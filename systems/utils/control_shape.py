import maya.cmds as cmds


def control_shape_list():
    return ["circle","cube","locator"]


class ControlTypes():
    def __init__(self, name, control_type):
        self.name = name
        module = f"self.create_{control_type}()"
        eval(module)

    def create_circle(self):
        self.ctrl_crv = cmds.circle(n=self.name,r=1, nr=(1, 0, 0))[0]
        return self.ctrl_crv

    def create_cube(self):
        self.ctrl_crv = cmds.curve(n=self.name,d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                                      (0,1,0),(1,1,0),(1,0,0),(1,1,0),(1,1,1),
                                                      (1,0,1),(1,1,1),(0,1,1),(0,0,1),(0,1,1),(0,1,0)])

        cmds.CenterPivot()
        cmds.xform(self.ctrl_crv,t=(-.5,-.5,-.5))
        cmds.xform(self.ctrl_crv,s=[5,5,5])
        return self.ctrl_crv

    def create_locator(self):
        self.ctrl_crv = cmds.spaceLocator(n=self.name)
        return self.ctrl_crv

    def return_ctrl(self):
        return self.ctrl_crv


class Controls():
    def __init__(self,scale,guide,ctrl_name,rig_type):
        self.ctrl_name = ctrl_name

        self.scale = scale
        if type(self.scale) is int or type(self.scale) is float:
            self.scale = [self.scale,self.scale,self.scale]

        control_type = cmds.getAttr(f"{guide}.{guide}_{rig_type}_control_shape",asString=1)
        if control_type in control_shape_list():
            control_module = ControlTypes(self.ctrl_name,control_type)
            self.ctrl = control_module.return_ctrl()
            self.set_control_size()
            self.set_name()

    def get_bounding_region(self):
        pass

    def set_control_size(self):
        cmds.xform(self.ctrl,s=[10*self.scale[0],10*self.scale[1],10*self.scale[2]])
        cmds.select(self.ctrl)
        cmds.makeIdentity(a=1,t=1,r=1,s=1)
        cmds.delete(self.ctrl, ch=1)

    def set_name(self):
        cmds.rename(self.ctrl,self.ctrl_name)

    def return_ctrl(self):
        return self.ctrl
