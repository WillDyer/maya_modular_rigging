import maya.cmds as cmds
from maya import OpenMayaUI as omui
import importlib

class CreateReverseFoot():
    def __init__(self, guides,accessed_module):
        self.attr_list = ["Rev_Foot_Dvdr","Roll","Bank","Heel_Twist","Toe_Twist"]
        print(f"GUIDES: {guides}")
        self.guides = guides
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        importlib.reload(self.module)

        # self.ui.create_locators.clicked.connect(self.create_loc)
        # self.ui.make_rev_foot.clicked.connect(self.create_system)

    def side(self):
        mirroring = False # tmp
        if mirroring == True:
            # side = self.system_to_be_made.side
            pass
        else: side = self.module.side
        return side

    def create_loc(self):
        print("create loc ran")
        side = self.side()
        rev_locators = self.module.rev_locators
        jnt_prefix = self.module.rev_locators["prefix"]

        if f"loc_{rev_locators['ankle']}{side}" in cmds.ls(f"loc_{rev_locators['ankle']}{side}"):
            cmds.error("ERROR: Item with the same name already exists.")

        loc_name = [f"rev_{rev_locators['ankle']}{side}",f"rev_{rev_locators['ball']}{side}",f"rev_{rev_locators['toe']}{side}"]
        locators_keys = rev_locators.values()
        jnt_name = [item for item in self.guides["ui_guide_list"] if any(key in item for key in locators_keys)]

        # jnt_name = [f"{jnt_prefix}_{rev_locators['ankle']}{side}",f"{jnt_prefix}_{rev_locators['ball']}{side}",f"{jnt_prefix}_{rev_locators['toe']}{side}"]
        for x in range(len(loc_name)):
            try:
                cmds.spaceLocator(n=f"loc_{loc_name[x]}")
                cmds.matchTransform(f"loc_{loc_name[x]}",jnt_name[x])
            except:
                cmds.error("Error: jnt_name cant be found check backend.")
        bank_in = f"loc_{rev_locators['bank_in']}{side}"
        bank_out = f"loc_{rev_locators['bank_out']}{side}"
        for x in [bank_in,bank_out]:
            cmds.spaceLocator(n=x)
            cmds.matchTransform(x, f"loc_rev_{rev_locators['ball']}{side}")
        offset = 10
        if bank_out[-2:] and bank_in[-2:] == "_l":
            cmds.move(offset,0,0,bank_out,r=1)
            cmds.move(-offset,0,0,bank_in,r=1)
        elif bank_out[-2:] and bank_in[-2:] == "_r":
            cmds.move(-offset,0,0,bank_out,r=1)
            cmds.move(offset,0,0,bank_in,r=1)
        else:
            cmds.error("No matching side suffex")


        cmds.spaceLocator(n=f"loc_{rev_locators['heel']}{side}")
        cmds.matchTransform(f"loc_{rev_locators['heel']}{side}",f"loc_rev_{rev_locators['ball']}{side}")
        cmds.move(0,0,-offset,f"loc_{rev_locators['heel']}{side}",r=1)
    
    def create_rev_jnts(self):
        side = self.side()
        jnt_list = [f"{self.ui.rev_heel.text()}{side}",f"{self.ui.rev_toe.text()}{side}",f"{self.ui.rev_ball.text()}{side}",f"{self.ui.rev_ankle.text()}{side}"]
        loc_list = [f"loc{self.ui.rev_heel.text()[3:]}{side}",f"loc{self.ui.rev_toe.text()[3:]}{side}",f"loc{self.ui.rev_ball.text()[3:]}{side}",f"loc{self.ui.rev_ankle.text()[3:]}{side}"]

        cmds.select(cl=1)
        for jnt in range(len(loc_list)):
            location = cmds.xform(loc_list[jnt], r=True, ws=True, q=True, t=True) # Gather locator location
            cmds.joint(n=jnt_list[jnt], p=location) # create joint based off the location

        # Orient joint
        cmds.joint(f"{jnt_list[0]}", edit=True, zso=1, oj="xyz", sao="xup", ch=True)
        # Orient end joint to world
        cmds.joint(f"{jnt_list[-1]}", e=True, oj="none" ,ch=True, zso=True)

        return jnt_list

    def foot_attr(self):
        #attr_list = ["Rev_Foot_Dvdr","Roll","Bank","Heel_Twist","Toe_Twist"]

        foot_ctrl = self.ui.foot_ctrl.text()
        if foot_ctrl in cmds.ls(foot_ctrl): # checking for ctrl
            pass
        else:
            cmds.error("Error: Foot control does not exist in scene")

        for attr in self.attr_list:
            attr_exists = cmds.attributeQuery(attr, node=foot_ctrl,ex=1)
            print(f"Exists: {attr_exists}")
            if attr_exists == False:
                if attr == self.attr_list[0]:
                    cmds.addAttr(foot_ctrl,ln=self.attr_list[0],at="enum",en="############",k=1)
                    cmds.setAttr(f"{foot_ctrl}.{self.attr_list[0]}",l=1)
                else:
                    cmds.addAttr(foot_ctrl, ln=attr, min=-20, max=20,k=1)
            else:
                print("Attribute Exists continuing")
                pass

        self.create_nodes(foot_ctrl)

    def create_condition_node(self, name):
        x = ""
        cmds.createNode("condition",n=name)
        for x in ["R","G","B"]:
            cmds.setAttr(f"{name}.colorIfFalse{x}",0)

    def create_nodes(self, foot_ctrl):
        #attr_list = ["Rev_Foot_Dvdr","Roll","Bank","Heel_Twist","Toe_Twist"]
        side = self.side()
        bank_in = self.ui.rev_bank_in.text()
        bank_out = self.ui.rev_bank_out.text()

        # BANK IN OUT
        self.create_condition_node(f"cond{self.ui.rev_bank_in.text()[3:]}{side}")
        self.create_condition_node(f"cond{self.ui.rev_bank_out.text()[3:]}{side}")
        for x in [bank_in,bank_out]:
            cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[2]}",f"cond{x[3:]}{side}.firstTerm")
            cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[2]}",f"cond{x[3:]}{side}.colorIfTrueR")

            cmds.shadingNode("floatMath",au=1,n=f"math{x[3:]}{side}")

            cmds.connectAttr(f"cond{x[3:]}{side}.outColorR",f"math{x[3:]}{side}.floatA")
            cmds.connectAttr(f"math{x[3:]}{side}.outFloat",f"loc{x[3:]}{side}.rotateX")

            cmds.setAttr(f"math{x[3:]}{side}.operation",2)
            cmds.setAttr(f"math{x[3:]}{side}.floatB",2.5)

        cmds.setAttr(f"cond{self.ui.rev_bank_in.text()[3:]}{side}.operation",2)
        cmds.setAttr(f"cond{self.ui.rev_bank_out.text()[3:]}{side}.operation",4)

        # HEEL & TOE TWIST
        heel_jnt = self.ui.rev_heel.text()
        toe_jnt = self.ui.rev_toe.text()
        for x in [heel_jnt, toe_jnt]:
            cmds.shadingNode("floatMath",au=1,n=f"math{x[3:]}{side}")

            cmds.connectAttr(f"math{x[3:]}{side}.outFloat",f"{x}{side}.rotateZ")

            cmds.setAttr(f"math{x[3:]}{side}.operation",2)
            cmds.setAttr(f"math{x[3:]}{side}.floatB",2.5)
        
        cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[3]}",f"math{heel_jnt[3:]}{side}.floatA")
        cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[4]}",f"math{toe_jnt[3:]}{side}.floatA")

        # ROLL
        ball_jnt = self.ui.rev_ball.text()
        self.create_condition_node(f"cond{ball_jnt[3:]}{side}")
        cmds.shadingNode("floatMath",au=1,n=f"math_roll{toe_jnt[3:]}{side}")
        cmds.shadingNode("floatMath",au=1,n=f"math_zeroed{ball_jnt[3:]}{side}")
        cmds.shadingNode("floatMath",au=1,n=f"math_reversed{ball_jnt[3:]}{side}")

        cmds.connectAttr(f"math_zeroed{ball_jnt[3:]}{side}.outFloat",f"cond{ball_jnt[3:]}{side}.colorIfTrueR")
        cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[1]}",f"cond{ball_jnt[3:]}{side}.firstTerm")
        cmds.connectAttr(f"cond{ball_jnt[3:]}{side}.outColorR",f"math_reversed{ball_jnt[3:]}{side}.floatA")

        cmds.connectAttr(f"math_roll{toe_jnt[3:]}{side}.outFloat",f"{toe_jnt}{side}.rotateY")
        cmds.connectAttr(f"math_reversed{ball_jnt[3:]}{side}.outFloat",f"{ball_jnt}{side}.rotateY")

        cmds.setAttr(f"math_roll{toe_jnt[3:]}{side}.operation",2)
        cmds.setAttr(f"math_roll{toe_jnt[3:]}{side}.floatB",4.5)
        cmds.setAttr(f"math_zeroed{ball_jnt[3:]}{side}.operation",1)
        cmds.setAttr(f"math_zeroed{ball_jnt[3:]}{side}.floatB",10)
        cmds.setAttr(f"math_reversed{ball_jnt[3:]}{side}.operation",2)
        cmds.setAttr(f"math_reversed{ball_jnt[3:]}{side}.floatB",-2.5)
        cmds.setAttr(f"cond{ball_jnt[3:]}{side}.operation",3)
        cmds.setAttr(f"cond{ball_jnt[3:]}{side}.secondTerm",10)
        
        cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[1]}",f"math_roll{toe_jnt[3:]}{side}.floatA")
        cmds.connectAttr(f"{foot_ctrl}.{self.attr_list[1]}",f"math_zeroed{ball_jnt[3:]}{side}.floatA")

    def create_system(self):
        side = self.side()
        parent_order = [f"{self.ui.rev_heel.text()}{side}",f"{self.ui.rev_toe.text()}{side}",f"loc{self.ui.rev_bank_in.text()[3:]}{side}",f"loc{self.ui.rev_bank_out.text()[3:]}{side}",f"{self.ui.rev_ball.text()}{side}",f"{self.ui.rev_ankle.text()}{side}"]
        parent_order.reverse()

        for loc in range(len(parent_order)):
            try:
                cmds.parent(f"loc{parent_order[loc][3:]}",f"loc{parent_order[loc+1][3:]}")
            except:
                pass

        rev_list = self.create_rev_jnts()
        jnt_list = [f"{self.ui.ankle_jnt.text()}{side}",f"{self.ui.ball_jnt.text()}{side}",f"{self.ui.toe_jnt.text()}{side}"]

        self.foot_attr()

        cmds.ikHandle(n=f"hdl_rev_ball{side}",sj=jnt_list[0],ee=jnt_list[1],sol="ikSCsolver")
        cmds.parent(f"hdl_rev_ball{side}",rev_list[2])
        cmds.ikHandle(n=f"hdl_rev_toe{side}",sj=jnt_list[1],ee=jnt_list[2],sol="ikSCsolver")
        cmds.parent(f"hdl_rev_toe{side}",rev_list[1])

        cmds.parent(rev_list[0],f"loc{self.ui.rev_ankle.text()[3:]}{side}")

        if self.ui.constraint_ankle_2_rev_jnt.isChecked() == True:
            cmds.parentConstraint(f"{self.ui.rev_ankle.text()}{side}",f"{self.ui.ankle_jnt.text()}{side}",n=f"pConst_{self.ui.foot_ctrl.text()}",mo=1)
        if self.ui.loc_2_rev_jnt.isChecked() == True:
            cmds.parent(f"{self.ui.ankle_hdl_jnt.text()}{side}",rev_list[3])


