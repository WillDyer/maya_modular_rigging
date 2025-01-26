import importlib
import maya.cmds as cmds
import json

from mod.guides import guide_data
importlib.reload(guide_data)

class ControlShapeList():
    def __init__(self):
        self.ctrl_shape_list = ["circle","cube","locator","custom"]

    def return_filtered_list(self, type, object):
        module = cmds.getAttr(f"{object}.base_module", asString=True)
        module_path = importlib.import_module(f"mod.modules.{module}")
        importlib.reload(module_path)

        base_guide = cmds.getAttr(f"{object}.original_guide", asString=True)

        try:
            try:
                if module_path.default_ctrl_shape[f"{type}_{base_guide}"]:
                    default_ctrl_shape = module_path.default_ctrl_shape[f"{type}_{base_guide}"]
                    if default_ctrl_shape in self.ctrl_shape_list:
                        self.ctrl_shape_list.remove(default_ctrl_shape)
                        self.ctrl_shape_list.insert(0, default_ctrl_shape)
            except AttributeError: pass  # catches if the module_path.default_ctrl_shape dict exists
        except KeyError: pass  # guide isnt in the default_ctrl_shape dict

    def return_list(self):
        return self.ctrl_shape_list


class ControlTypes():
    def __init__(self, name="", control_type="", guide=""):
        self.name = name
        self.guide = guide
        module = f"self.create_{control_type}()"
        eval(module)

    def create_circle(self):
        self.ctrl_crv = cmds.circle(n=self.name,r=10, nr=(1, 0, 0), ch=False)[0]
        return self.ctrl_crv

    def create_cube(self):
        self.ctrl_crv = cmds.curve(n=self.name,d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                                      (0,1,0),(1,1,0),(1,0,0),(1,1,0),(1,1,1),
                                                      (1,0,1),(1,1,1),(0,1,1),(0,0,1),(0,1,1),(0,1,0)])

        cmds.CenterPivot()
        cmds.xform(self.ctrl_crv,t=(-.5,-.5,-.5))
        cmds.xform(self.ctrl_crv,s=[5,5,5])
        cmds.xform(self.ctrl_crv,s=[10,10,10])
        cmds.select(self.ctrl_crv)
        cmds.makeIdentity(a=1,t=1,r=1,s=1)
        cmds.delete(self.ctrl_crv, ch=1)
        return self.ctrl_crv

    def create_locator(self):
        self.ctrl_crv = cmds.spaceLocator(n=self.name)
        cmds.xform(self.ctrl_crv,s=[10,10,10])
        cmds.select(self.ctrl_crv)
        cmds.makeIdentity(a=1,t=1,r=1,s=1)
        cmds.delete(self.ctrl_crv, ch=1)
        return self.ctrl_crv

    def create_custom(self):
        if cmds.attributeQuery("ctrl_data", node=self.guide, exists=True):
            retrieved_data = cmds.getAttr(f"{self.guide}.ctrl_data")
            control_data = json.loads(retrieved_data)

        if self.name in control_data.keys():
            key = control_data[self.name]
            ctrl = self.name
            if not cmds.objExists(self.name):
                ctrl = cmds.createNode("transform", n=self.name)

            cmds.xform(ctrl, t=[0, 0, 0], ws=True)
            cmds.xform(ctrl, ro=[0, 0, 0], ws=True)
            cmds.xform(ctrl, s=[1, 1, 1], ws=True)

            # Recreate shapes
            for shape in key["shapes"]:
                print(shape["type"])
                if shape["type"] == "nurbsCurve":
                    new_shape = cmds.curve(d=shape["degree"], p=shape["cvs"])
                    new_shape_node = cmds.listRelatives(new_shape, shapes=True, fullPath=True)[0]
                    cmds.parent(new_shape_node, ctrl, shape=True, relative=True)
                    cmds.delete(new_shape)
                elif shape["type"] == "mesh":
                    new_shape = cmds.polyCreateFacet(p=shape["vertices"])
                elif shape["type"] == "circle":
                    center = shape['center']
                    radius = shape['radius']
                    new_shape = cmds.circle(radius=radius, nr=(1,0,0), ch=False)
                    new_shape_node = cmds.listRelatives(new_shape, shapes=True, fullPath=True)[0]
                    new_shape_node = cmds.rename(new_shape_node, f"{ctrl}Shape")
                    cmds.parent(new_shape_node, ctrl, shape=True, relative=True)
                    cmds.delete(new_shape)
                    cvs_new = cmds.ls(f"{new_shape_node}.cv[*]", flatten=True)
                    print(len(shape['cvs']))
                    if len(cvs_new) != len(shape['cvs']):
                        cmds.error("cvs dont match")

                    for i, cv in enumerate(cvs_new):
                        cmds.xform(cv, translation=shape["cvs"][i], os=True)


            self.ctrl_crv = ctrl

    def return_ctrl(self):
        return self.ctrl_crv



class Controls():
    def __init__(self,scale,guide="",ctrl_name="",rig_type="",ctrl_shape="", associated_guide=None):
        self.ctrl_name = ctrl_name

        self.scale = scale
        if type(self.scale) is int or type(self.scale) is float:
            self.scale = [self.scale,self.scale,self.scale]

        if guide:
            control_type = cmds.getAttr(f"{guide}.{guide}_{rig_type}_control_shape",asString=1)
        else:
            if ctrl_shape:
                control_type = ctrl_shape
            else:
                raise AttributeError("control_shape: error ctrl_shape flag not entered when not using guide flag")

        ctrl_shape_instance = ControlShapeList()
        ctrl_list = ctrl_shape_instance.return_list()

        if control_type in ctrl_list:
            if control_type == "custom":
                control_module = ControlTypes(name=self.ctrl_name, control_type=control_type, guide=guide)
            else:
                control_module = ControlTypes(name=self.ctrl_name, control_type=control_type)
            self.ctrl = control_module.return_ctrl()
            self.set_control_size()
            self.set_name()

        if associated_guide:
            cmds.addAttr(self.ctrl,ln="associated_guide", at="enum",en=associated_guide, k=False)
            # guide_data.capture_control_data(ctrl=self.ctrl, use_associated=True)
        elif guide:
            cmds.addAttr(self.ctrl,ln="associated_guide",at="enum",en=guide,k=False)
            # guide_data.capture_control_data(ctrl=self.ctrl, guide=guide)
        else:
            print("control_shape: couldnt find guide or associated_guide")

    def get_bounding_region(self):
        pass

    def set_control_size(self):
        cmds.xform(self.ctrl,s=[self.scale[0],self.scale[1],self.scale[2]])
        cmds.select(self.ctrl)
        cmds.makeIdentity(a=1,t=1,r=1,s=1)
        cmds.delete(self.ctrl, ch=1)

    def set_name(self):
        self.ctrl = cmds.rename(self.ctrl,self.ctrl_name)

    def return_ctrl(self):
        return self.ctrl
