import maya.cmds as cmds
from maya import OpenMayaUI as omui
import importlib

class CreateReverseLocators():
    def __init__(self, guides,accessed_module):
        self.guides = guides
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        importlib.reload(self.module)
        self.locator_list = self.create_loc()

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
        loc_prefix = "loc_rev"

        if f"loc_{rev_locators['ankle']}{side}" in cmds.ls(f"loc_{rev_locators['ankle']}{side}"):
            cmds.error("ERROR: Item with the same name already exists.")

        loc_name = [f"rev_{rev_locators['toe']}{side}",f"rev_{rev_locators['ball']}{side}",f"rev_{rev_locators['ankle']}{side}"]
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
            cmds.matchTransform(x, f"{loc_prefix}_{rev_locators['ball']}{side}")
        offset = 10
        if bank_out[-2:] and bank_in[-2:] == "_l":
            cmds.move(offset,0,0,bank_out,r=1)
            cmds.move(-offset,0,0,bank_in,r=1)
        elif bank_out[-2:] and bank_in[-2:] == "_r":
            cmds.move(-offset,0,0,bank_out,r=1)
            cmds.move(offset,0,0,bank_in,r=1)
        else:
            cmds.error("No matching side suffex")

        loc_heel = cmds.spaceLocator(n=f"{loc_prefix}_{rev_locators['heel']}{side}")[0]
        cmds.matchTransform(f"{loc_prefix}_{rev_locators['heel']}{side}",f"{loc_prefix}_{rev_locators['ball']}{side}")
        cmds.move(0,0,-offset,f"{loc_prefix}_{rev_locators['heel']}{side}",r=1)

        loc_list = [loc_heel,f"{loc_prefix}_{rev_locators['toe']}{side}",f"{loc_prefix}_{rev_locators['ball']}{side}",f"{loc_prefix}_{rev_locators['ankle']}{side}",bank_in, bank_out]
        return loc_list

    def get_locators(self):
        return self.locator_list

class CreateReverseFoot():
    def __init__(self, accessed_module, system):
        self.attr_list = ["Rev_Foot_Dvdr","Roll","Bank","Heel_Twist","Toe_Twist"]
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        importlib.reload(self.module)
        self.system = system
        self.reverse_foot_data = {
            "loc_heel": self.system["rev_locators"][0],
            "loc_toe": self.system["rev_locators"][1],
            "loc_ball": self.system["rev_locators"][2],
            "loc_ankle": self.system["rev_locators"][3],
            "bank_in": self.system["rev_locators"][4],
            "bank_out": self.system["rev_locators"][5],
        }

        self.create_system()

    def side(self):
        mirroring = False # tmp
        if mirroring == True:
            # side = self.system_to_be_made.side
            pass
        else: side = self.module.side
        return side
    
    def create_rev_jnts(self):
        side = self.side()
        jnt_list = [f"jnt{self.reverse_foot_data['loc_heel'][3:]}",f"jnt{self.reverse_foot_data['loc_toe'][3:]}",f"jnt{self.reverse_foot_data['loc_ball'][3:]}",f"jnt{self.reverse_foot_data['loc_ankle'][3:]}"]
        loc_list = [self.reverse_foot_data["loc_heel"],self.reverse_foot_data["loc_toe"],self.reverse_foot_data["loc_ball"],self.reverse_foot_data["loc_ankle"]]

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
        if self.foot_ctrl in cmds.ls(self.foot_ctrl): # checking for ctrl
            pass
        else:
            cmds.error("Error: Foot control does not exist in scene")

        for attr in self.attr_list:
            attr_exists = cmds.attributeQuery(attr, node=self.foot_ctrl,ex=1)
            print(f"Exists: {attr_exists}")
            if attr_exists == False:
                if attr == self.attr_list[0]:
                    cmds.addAttr(self.foot_ctrl,ln=self.attr_list[0],at="enum",en="############",k=1)
                    cmds.setAttr(f"{self.foot_ctrl}.{self.attr_list[0]}",l=1)
                else:
                    cmds.addAttr(self.foot_ctrl, ln=attr, min=-20, max=20,k=1)
            else:
                print("Attribute Exists continuing")
                pass

        self.create_nodes()

    def create_condition_node(self, name):
        x = ""
        node_name = cmds.createNode("condition",n=name)
        for x in ["R","G","B"]:
            cmds.setAttr(f"{name}.colorIfFalse{x}",0)
        return node_name

    def create_nodes(self):
        side = self.side()
        bank_in = self.reverse_foot_data["bank_in"]
        bank_out = self.reverse_foot_data["bank_out"]

        # BANK IN OUT
        bank_in_node = self.create_condition_node(f"cond_{bank_in}")
        bank_out_node = self.create_condition_node(f"cond_{bank_out}")
        for x in [bank_in,bank_out]:
            cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[2]}",f"cond_{x}.firstTerm")
            cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[2]}",f"cond_{x}.colorIfTrueR")

            cmds.shadingNode("floatMath",au=1,n=f"math_{x}")

            cmds.connectAttr(f"cond_{x}.outColorR",f"math_{x}.floatA")
            cmds.connectAttr(f"math_{x}.outFloat",f"{x}.rotateX")

            cmds.setAttr(f"math_{x}.operation",2)
            cmds.setAttr(f"math_{x}.floatB",2.5)

        cmds.setAttr(f"cond_{bank_in}.operation",2)
        cmds.setAttr(f"cond_{bank_out}.operation",4)

        # HEEL & TOE TWIST
        heel_jnt = f"jnt{self.reverse_foot_data['loc_heel'][3:]}"
        toe_jnt = f"jnt{self.reverse_foot_data['loc_toe'][3:]}"
        for x in [heel_jnt, toe_jnt]:
            cmds.shadingNode("floatMath",au=1,n=f"math_{x}")

            cmds.connectAttr(f"math_{x}.outFloat",f"{x}.rotateZ")

            cmds.setAttr(f"math_{x}.operation",2)
            cmds.setAttr(f"math_{x}.floatB",2.5)
        
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[3]}",f"math_{heel_jnt}.floatA")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[4]}",f"math_{toe_jnt}.floatA")

        # ROLL
        ball_jnt = f"jnt{self.reverse_foot_data['loc_ball'][3:]}"
        self.create_condition_node(f"cond_{ball_jnt}")
        cmds.shadingNode("floatMath",au=1,n=f"math_roll_{toe_jnt}")
        cmds.shadingNode("floatMath",au=1,n=f"math_zeroed_{ball_jnt}")
        cmds.shadingNode("floatMath",au=1,n=f"math_reversed_{ball_jnt}")

        cmds.connectAttr(f"math_zeroed_{ball_jnt}.outFloat",f"cond_{ball_jnt}.colorIfTrueR")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"cond_{ball_jnt}.firstTerm")
        cmds.connectAttr(f"cond_{ball_jnt}.outColorR",f"math_reversed_{ball_jnt}.floatA")

        cmds.connectAttr(f"math_roll_{toe_jnt}.outFloat",f"{toe_jnt}.rotateY")
        cmds.connectAttr(f"math_reversed_{ball_jnt}.outFloat",f"{ball_jnt}.rotateY")

        cmds.setAttr(f"math_roll_{toe_jnt}.operation",2)
        cmds.setAttr(f"math_roll_{toe_jnt}.floatB",4.5)
        cmds.setAttr(f"math_zeroed_{ball_jnt}.operation",1)
        cmds.setAttr(f"math_zeroed_{ball_jnt}.floatB",10)
        cmds.setAttr(f"math_reversed_{ball_jnt}.operation",2)
        cmds.setAttr(f"math_reversed_{ball_jnt}.floatB",-2.5)
        cmds.setAttr(f"cond_{ball_jnt}.operation",3)
        cmds.setAttr(f"cond_{ball_jnt}.secondTerm",10)
        
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"math_roll_{toe_jnt}.floatA")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"math_zeroed_{ball_jnt}.floatA")

    def create_system(self):
        side = self.side()
        parent_order = [self.reverse_foot_data["loc_heel"],self.reverse_foot_data["loc_toe"],self.reverse_foot_data["bank_in"],self.reverse_foot_data["bank_out"],self.reverse_foot_data["loc_ball"],self.reverse_foot_data["loc_ankle"]]
        parent_order.reverse()

        for loc in range(len(parent_order)):
            try:
                cmds.parent(parent_order[loc],parent_order[loc+1])
            except:
                pass

        rev_list = self.create_rev_jnts()
        #jnt_list = [f"{self.ui.ankle_jnt.text()}{side}",f"{self.ui.ball_jnt.text()}{side}",f"{self.ui.toe_jnt.text()}{side}"]
        jnt_verification_values = ["ankle","ball","toe"]
        jnt_list = [item for item in self.system["ik_joint_list"] if any(key in item for key in jnt_verification_values)]

        self.foot_ctrl = [x for x in self.system["ik_ctrl_list"] if cmds.attributeQuery("handle", node=x, exists=True) and cmds.getAttr(f"{x}.handle", asString=1) == "True"][0]
        self.foot_attr()

        cmds.ikHandle(n=f"hdl_rev_ball{side}",sj=jnt_list[0],ee=jnt_list[1],sol="ikSCsolver")
        cmds.parent(f"hdl_rev_ball{side}",rev_list[2])
        cmds.ikHandle(n=f"hdl_rev_toe{side}",sj=jnt_list[1],ee=jnt_list[2],sol="ikSCsolver")
        cmds.parent(f"hdl_rev_toe{side}",rev_list[1])

        cmds.parent(rev_list[0],self.reverse_foot_data["loc_ankle"])

        #cmds.parentConstraint(self.reverse_foot_data["loc_ankle"],f"jnt{self.reverse_foot_data['loc_ankle'][3:]}",n=f"pConst_{self.foot_ctrl}",mo=1)
        #cmds.parent(self.system["ik_handle"],rev_list[3])
