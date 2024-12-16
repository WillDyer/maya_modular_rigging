import maya.cmds as cmds


class CreateSquashAndStretch():
    def __init__(self, key, validation_joints):
        self.key = key
        self.validation_joints = validation_joints
        self.name_definition()
        if cmds.getAttr(f"{self.end_control}.handle",asString=1) == "True":  # checking it is the end handle ctrl
            self.create_nodes()
            self.create_attributes()
            self.connect_nodes()

    def name_definition(self):
        for joint in self.key["ik_joint_list"]:
            if self.validation_joints["start_joint"] in joint:
                self.start_joint = joint
            elif self.validation_joints["pv_joint"] in joint:
                self.pv_joint = joint
            elif self.validation_joints["end_joint"] in joint:
                self.end_joint = joint

        for guide in self.key["guide_list"]:
            if self.validation_joints["start_joint"] in guide:
                self.start_guide = guide
                self.start_control = f"ctrl_ik_{self.start_guide}"
            elif self.validation_joints["end_joint"] in guide:
                self.end_guide = guide
                self.end_control = f"ctrl_ik_{self.end_guide}"

    def create_nodes(self):
        self.distancebetween_node = cmds.shadingNode("distanceBetween",au=1,n=f"{self.end_guide}_distanceBetween")
        self.scalefactor_node = cmds.shadingNode("multiplyDivide",au=1, n=f"{self.end_guide}_scaleFactor")
        self.conditionoperation_node = cmds.shadingNode("plusMinusAverage",au=1, n=f"{self.end_guide}_conditionOperation")
        self.shapepresavation_node = cmds.shadingNode("multiplyDivide",au=1, n=f"{self.end_guide}_shapePresavation")
        self.stretchblend_node = cmds.shadingNode("blendColors",au=1,n=f"{self.end_guide}_stretchBlend")
        self.stretchikblend_node = cmds.shadingNode("blendColors",au=1,n=f"{self.end_guide}_stretchIkBlend")
        self.stretchtype_node = cmds.createNode("condition",n=f"{self.end_guide}_stretchType")

    def create_attributes(self):
        cmds.addAttr(self.end_control,k=1,ln="stretchiness",nn="Stretchiness",at="float",min=0)
        cmds.addAttr(self.end_control,k=1,ln="stretch_type",nn="Stretch Type",at="enum",en="Both:Stretch:Squash")

    def connect_nodes(self):
        # connect ctrls to distance
        locator = cmds.spaceLocator(n=f"loc_{self.end_guide}_stretchEnd")[0]
        cmds.matchTransform(locator, self.end_control)
        cmds.parent(locator, self.end_control)
        cmds.connectAttr(f"{self.start_control}.worldMatrix", f"{self.distancebetween_node}.inMatrix1", f=1)
        cmds.connectAttr(f"{locator}.worldMatrix", f"{self.distancebetween_node}.inMatrix2", f=1)

        # scale factor node
        cmds.connectAttr(f"{self.distancebetween_node}.distance", f"{self.scalefactor_node}.input1X")
        cmds.setAttr(f"{self.scalefactor_node}.operation",2)
        value = cmds.getAttr(f"{self.scalefactor_node}.input1X")
        cmds.setAttr(f"{self.scalefactor_node}.input2X", value)

        # stretch blend node
        cmds.connectAttr(f"{self.scalefactor_node}.outputX",f"{self.stretchblend_node}.color1R")
        cmds.connectAttr(f"{self.end_control}.stretchiness",f"{self.stretchblend_node}.blender")
        for rgb in ["R","G","B"]: cmds.setAttr(f"{self.stretchblend_node}.color2{rgb}",1)

        # condition operation node
        cmds.setAttr(f"{self.conditionoperation_node}.input1D[0]",1)
        cmds.connectAttr(f"{self.end_control}.stretch_type",f"{self.conditionoperation_node}.input1D[1]",f=1)
        cmds.connectAttr(f"{self.end_control}.stretch_type",f"{self.conditionoperation_node}.input1D[2]",f=1)

        # stretch type node
        cmds.connectAttr(f"{self.scalefactor_node}.outputX",f"{self.stretchtype_node}.firstTerm")
        cmds.connectAttr(f"{self.stretchblend_node}.outputR",f"{self.stretchtype_node}.colorIfTrueR")
        cmds.connectAttr(f"{self.conditionoperation_node}.output1D",f"{self.stretchtype_node}.operation")
        cmds.setAttr(f"{self.stretchtype_node}.secondTerm",1)

        # shape presavation node
        cmds.connectAttr(f"{self.stretchtype_node}.outColorR",f"{self.shapepresavation_node}.input1X")
        cmds.setAttr(f"{self.shapepresavation_node}.input2X", -1)
        cmds.setAttr(f"{self.shapepresavation_node}.operation", 3)

        # stretch ik blend node
        cmds.connectAttr(f"{self.shapepresavation_node}.outputX",f"{self.stretchikblend_node}.color2G")
        cmds.connectAttr(f"{self.stretchtype_node}.outColorR",f"{self.stretchikblend_node}.color2R")
        cmds.setAttr(f"{self.stretchikblend_node}.color1G",1)
        if cmds.attributeQuery("ikfk_switch_name", node=self.end_control, exists=True):
            ikfk_switch_attr = cmds.getAttr(f"{self.end_control}.ikfk_switch_name", asString=1)
            cmds.connectAttr(f"{self.end_control}.{ikfk_switch_attr}",f"{self.stretchikblend_node}.blender")
        else:
            cmds.setAttr(f"{self.stretchikblend_node}.blender",0)

        # connect to joint scale
        cmds.connectAttr(f"{self.stretchikblend_node}.outputR",f"{self.start_joint}.scaleX")
        cmds.connectAttr(f"{self.stretchikblend_node}.outputR",f"{self.pv_joint}.scaleX")
        cmds.connectAttr(f"{self.stretchikblend_node}.outputG",f"{self.start_joint}.scaleY")
        cmds.connectAttr(f"{self.stretchikblend_node}.outputG",f"{self.pv_joint}.scaleY")
        cmds.connectAttr(f"{self.stretchikblend_node}.outputG",f"{self.start_joint}.scaleZ")
        cmds.connectAttr(f"{self.stretchikblend_node}.outputG",f"{self.pv_joint}.scaleZ")
