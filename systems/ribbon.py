import maya.cmds as cmds
import maya.OpenMaya as om
import importlib
import math

from systems.utils import (OPM, utils)

importlib.reload(OPM)
importlib.reload(utils)


class create_ribbon():
    def __init__(self, system, accessed_module, ctrl_amount):
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        importlib.reload(self.module)
        self.ctrl_amount = ctrl_amount
        self.system = system
        self.scale = 10 * self.module.guide_scale
        self.create_ribbon()

    def create_ribbon(self):
        self.nurbs_curve = self.create_nurbs_curve()

        self.top_grp = cmds.group(n=f"grp_parent_ribbon_{self.system['master_guide']}", em=1)
        self.base_ribbon()
        self.create_controllers()
        self.group_setup()
        self.skin_ribbon()
        self.constrain_to_ik_joints()
        cmds.group(self.system["ik_joint_list"], n=f"grp_ik_jnts_{self.system['master_guide']}", w=1)
        cmds.parent(self.nurbs_curve, f"grp_parent_ribbon_{self.system['master_guide']}")
        cmds.select(clear=1)

    def create_nurbs_curve(self):
        start_joint = [x for x in self.system["ik_joint_list"] if self.module.ik_joints["start_joint"] in x][0]
        end_joint = [x for x in self.system["ik_joint_list"] if self.module.ik_joints["end_joint"] in x][0]
        # self.joint_chain = self.get_joints_between(start_joint, end_joint)
        self.joint_chain = utils.get_joints_between(start_joint, end_joint)

        positions = []
        for joint in self.joint_chain:
            pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
            positions.append(pos)

        curves = []

        offset_positions_left = []
        offset_positions_right = []
        for pos in positions:
            offset_positions_left.append([pos[0] - (5 * self.module.guide_scale), pos[1], pos[2]])
            offset_positions_right.append([pos[0] + (5 * self.module.guide_scale), pos[1], pos[2]])
        curve_left = cmds.curve(degree=1, point=offset_positions_left)
        curve_right = cmds.curve(degree=1, point=offset_positions_right)
        curves.append(curve_left)
        curves.append(curve_right)

        nurbs_curve = cmds.loft(curves, degree=3, ch=False, uniform=True)[0]
        nurbs_curve = cmds.rebuildSurface(nurbs_curve, rt=0, kr=2, dir=2, kc=0, su=0, sv=0)
        nurbs_curve = cmds.rename(nurbs_curve, f"ribbon_{self.system['master_guide']}")
        cmds.delete(curves)

        return nurbs_curve

    def get_joints_between(self, start_joint, end_joint):
        print("GET JOINTS BETWEEN RAN")
        # Ensure both joints exist
        if not cmds.objExists(start_joint) or not cmds.objExists(end_joint):
            raise ValueError("One or both of the specified joints do not exist.")

        # Get the full path for both joints
        start_path = cmds.ls(start_joint, long=True)[0]
        end_path = cmds.ls(end_joint, long=True)[0]

        # Split the paths into individual joint names
        start_joints = start_path.split('|')[1:]  # Exclude the root '|'
        end_joints = end_path.split('|')[1:]      # Exclude the root '|'

        # Find the common ancestor
        common_ancestor = None
        for sj, ej in zip(start_joints, end_joints):
            if sj == ej:
                common_ancestor = sj
            else:
                break

        if common_ancestor is None:
            raise ValueError("The specified joints do not share a common ancestor.")

        # Build the path from start_joint to common_ancestor
        start_to_common = start_joints[start_joints.index(common_ancestor):]

        # Build the path from common_ancestor to end_joint (reverse order)
        common_to_end = end_joints[end_joints.index(common_ancestor)+1:]

        # Combine the paths
        joint_path = start_to_common + common_to_end

        return joint_path

    def param_from_length(self, curve, count, curve_type="open", space="uv", normalized=True, delete_curve=True):

        if curve_type == "periodic":
            divider = count
        else:
            divider = count - 1

        if divider == 0:
            divider = 1

        dag = om.MDagPath()
        obj = om.MObject()
        crv = om.MSelectionList()
        crv.add(curve)
        crv.getDagPath(0, dag, obj)

        curve_fn = om.MFnNurbsCurve(dag)
        length = curve_fn.length()

        param = [curve_fn.findParamFromLength(i * ((1 / float(divider)) * length)) for i in range(count)]

        if space == "world":
            data = []
            space = om.MSpace.kWorld
            point = om.MPoint()
            for p in param:
                curve_fn.getPointAtParam(p, point, space)
                data.append([point[0], point[1], point[2]])  # world space points
        elif normalized is True:
            def normalizer(value, old_range, new_range):
                return (value - old_range[0]) * (new_range[1] - new_range[0]) / (old_range[1] - old_range[0]) + new_range[0]

            max_v = cmds.getAttr(curve + ".minMaxValue.maxValue")
            min_v = cmds.getAttr(curve + ".minMaxValue.minValue")

            data = [normalizer(p, [min_v, max_v], [0, 1]) for p in param]
        else:
            data = param

        if delete_curve:
            cmds.delete(curve)
        else:
            pass
        return data

    def base_ribbon(self):
        # Collect span count
        surface = cmds.listRelatives(self.nurbs_curve, s=1)[0]

        self.spansU = cmds.getAttr(f"{self.nurbs_curve}.spansU")
        self.spansV = cmds.getAttr(f"{self.nurbs_curve}.spansV")

        # selected surface is periodic or open? (cylinder or a plane)
        if cmds.getAttr(surface + ".formU") == 2 or cmds.getAttr(surface + ".formV") == 2:  # Check for closed
            curve_type = "periodic"
            spans = self.spansV
        elif cmds.getAttr(surface + ".formU") == 0 or cmds.getAttr(surface + ".formV") == 0:  # check not closed
            curve_type = "open"
            spans = self.spansV + 1

        u_curve_corr = cmds.duplicateCurve(self.nurbs_curve + ".v[.5]", local=True, ch=0)[0]
        param_ctrls = self.param_from_length(u_curve_corr, spans, curve_type, "uv", delete_curve=False)
        self.skn_ctrls = self.param_from_length(u_curve_corr, self.ctrl_amount, curve_type, "uv", delete_curve=True)

        self.fol_jnt_list = []
        self.fol_shape_list = []
        self.fol_parent_list = []
        for x in range(spans):
            fol_shape = cmds.createNode("follicle")
            fol_parent = cmds.listRelatives(fol_shape, p=True)[0]
            fol_parent = cmds.rename(fol_parent, f"fol{self.joint_chain[spans-1][3:]}")
            fol_shape = cmds.listRelatives(fol_parent, c=True)[0]
            cmds.setAttr(fol_shape + ".visibility", 1)

            cmds.setAttr(f"{fol_shape}.simulationMethod", 0)

            cmds.connectAttr(f"{surface}.worldMatrix[0]", f"{fol_shape}.inputWorldMatrix")
            cmds.connectAttr(f"{surface}.local", f"{fol_shape}.inputSurface")

            cmds.connectAttr(f"{fol_shape}.outRotate", f"{fol_parent}.rotate")
            cmds.connectAttr(f"{fol_shape}.outTranslate", f"{fol_parent}.translate")

            cmds.setAttr(f"{fol_shape}.parameterV", param_ctrls[x])
            cmds.setAttr(f"{fol_shape}.parameterU", 0.5)

            cmds.select(fol_parent)
            joint = cmds.joint(n=f"jnt_{fol_parent}")

            self.fol_jnt_list.append(joint)
            self.fol_shape_list.append(fol_shape)
            self.fol_parent_list.append(fol_parent)

    def create_controllers(self):
        cmds.select(cl=1)

        self.ctrl_list = []
        self.skn_jnt_list = []

        fol_list_int = len(self.fol_parent_list)
        for x in self.skn_ctrls:
            item = fol_list_int * x
            item = math.ceil(item)
            if item == 0:
                item = 1

            selected_follicle = self.fol_parent_list[item-1]
            cmds.select(selected_follicle)
            joint = cmds.joint(n=f"jnt_ctrl{selected_follicle[3:]}", r=3)
            cmds.parent(joint, world=True)
            cmds.select(cl=1)
            self.skn_jnt_list.append(joint)

            ctrl = f"ctrl{selected_follicle[3:]}"
            cmds.circle(n=ctrl, r=self.scale, nr=(0, 1, 0))  # temporary, will make interchangable
            cmds.matchTransform(ctrl, joint)
            cmds.parentConstraint(ctrl, joint, mo=1, n=f"pConst_{joint}")
            cmds.connectAttr(f"{ctrl}.scale", f"{joint}.scale")
            cmds.select(ctrl)
            OPM.offsetParentMatrix(ctrl)
            self.ctrl_list.append(ctrl)

    def group_setup(self):
        cmds.group(self.ctrl_list, n=f"grp_ctrl_ribbon_{self.system['master_guide']}", p=self.top_grp)
        cmds.group(self.skn_jnt_list, n=f"grp_ribbon_{self.system['master_guide']}_skn_jnt", p=self.top_grp)
        cmds.group(self.fol_parent_list, n=f"grp_ribbon_{self.system['master_guide']}_fol", p=self.top_grp)

    def skin_ribbon(self):
        cmds.skinCluster(self.skn_jnt_list, self.nurbs_curve)

    def constrain_to_ik_joints(self):
        for joint in range(len(self.system["ik_joint_list"])):
            try:
                cmds.parentConstraint(self.fol_jnt_list[joint], self.system["ik_joint_list"][joint], mo=1, n=f"pConst_{self.fol_jnt_list[joint]}")
            except:
                pass

    def get_ribbon_ctrls(self):
        return self.ctrl_list
