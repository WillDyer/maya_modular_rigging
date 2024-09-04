import maya.cmds as cmds
import importlib


class CreateReverseLocators():
    def __init__(self, guides,accessed_module):
        self.guides = guides
        self.accessed_module = accessed_module
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        importlib.reload(self.module)
        self.locator_list = self.create_loc()

    def side(self):
        mirroring = False  # tmp
        if mirroring is True:
            # side = self.system_to_be_made.side
            pass
        else: side = self.module.side
        return side

    def create_loc(self):
        side = self.side()
        rev_locators = self.module.rev_locators
        loc_prefix = "loc_rev"

        if f"loc_{rev_locators['ankle']}{side}" in cmds.ls(f"loc_{rev_locators['ankle']}{side}"):
            cmds.error("ERROR: Item with the same name already exists.")

        # loc_name = [f"rev_{rev_locators['toe']}{side}",f"rev_{rev_locators['ball']}{side}",f"rev_{rev_locators['ankle']}{side}"]
        locators_keys = rev_locators.values()
        jnt_name = [item for item in self.guides["ui_guide_list"] if any(key in item for key in locators_keys)]
        loc_name = [f"loc_rev_{item}" for item in self.guides["ui_guide_list"] if any(key in item for key in locators_keys)]
        # list order needs to be: toe, ball, ankle
        loc_toe = loc_name[0]
        loc_ball = loc_name[1]
        loc_ankle = loc_name[2]

        for x in range(len(loc_name)):
            try:
                cmds.spaceLocator(n=loc_name[x])
                cmds.matchTransform(loc_name[x],jnt_name[x])
            except:
                cmds.error("Error: jnt_name cant be found check backend.")
        bank_in = f"loc_{rev_locators['bank_in']}"
        bank_out = f"loc_{rev_locators['bank_out']}"
        for x in [bank_in,bank_out]:
            tmp = cmds.spaceLocator(n=f"{x}{side}_#")[0]
            cmds.matchTransform(tmp, loc_ball)
            if x == bank_in: bank_in = tmp
            elif x == bank_out: bank_out = tmp
        offset = 10
        bank_out_split = bank_out.split("_")[-2]
        bank_in_split = bank_out.split("_")[-2]
        if bank_out_split and bank_in_split == "l":
            cmds.move(offset,0,0,bank_out,r=1)
            cmds.move(-offset,0,0,bank_in,r=1)
        elif bank_out_split and bank_in_split == "r":
            cmds.move(-offset,0,0,bank_out,r=1)
            cmds.move(offset,0,0,bank_in,r=1)
        else:
            cmds.error("No matching side suffex")

        loc_heel = cmds.spaceLocator(n=f"{loc_prefix}_{rev_locators['heel']}{side}_#")[0]
        cmds.matchTransform(loc_heel,loc_ball)
        cmds.move(0,0,-offset,loc_heel,r=1)

        loc_list = [loc_heel,loc_toe,loc_ball,loc_ankle,bank_in, bank_out]
        ankle_guide = [guide for guide in self.guides["ui_guide_list"] if self.module.rev_locators["ankle"] in guide][0]
        grp = cmds.group(loc_list, n=f"grp_rev_loc_{ankle_guide}")
        constraint_name = cmds.parentConstraint(ankle_guide, grp, mo=1, n=f"pConst_{ankle_guide}")[0]
        cmds.setAttr(f"{constraint_name}.hiddenInOutliner", True)
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
        side = self.system['side']
        return side

    def create_rev_jnts(self):
        side = self.side()
        jnt_list = [f"jnt{self.reverse_foot_data['loc_heel'][3:]}",
                    f"jnt{self.reverse_foot_data['loc_toe'][3:]}",
                    f"jnt{self.reverse_foot_data['loc_ball'][3:]}",
                    f"jnt{self.reverse_foot_data['loc_ankle'][3:]}"]
        loc_list = [self.reverse_foot_data["loc_heel"],
                    self.reverse_foot_data["loc_toe"],
                    self.reverse_foot_data["loc_ball"],
                    self.reverse_foot_data["loc_ankle"]]

        cmds.select(cl=1)
        for jnt in range(len(loc_list)):
            location = cmds.xform(loc_list[jnt], r=True, ws=True, q=True, t=True)  # Gather locator location
            cmds.joint(n=jnt_list[jnt], p=location)  # create joint based off the location

        # Orient joint
        cmds.joint(f"{jnt_list[0]}", edit=True, zso=1, oj="xyz", sao="xup", ch=True)
        # Orient end joint to world
        cmds.joint(f"{jnt_list[-1]}", e=True, oj="none",ch=True, zso=True)

        return jnt_list

    def foot_attr(self):
        if self.foot_ctrl in cmds.ls(self.foot_ctrl):  # checking for ctrl
            pass
        else:
            cmds.error("Error: Foot control does not exist in scene")

        for attr in self.attr_list:
            attr_exists = cmds.attributeQuery(attr, node=self.foot_ctrl,ex=1)
            if attr_exists is False:
                if attr == self.attr_list[0]:
                    cmds.addAttr(self.foot_ctrl,ln=self.attr_list[0],at="enum",en="############",k=1)
                    cmds.setAttr(f"{self.foot_ctrl}.{self.attr_list[0]}",l=1)
                else:
                    cmds.addAttr(self.foot_ctrl, ln=attr, min=-20, max=20,k=1)
            else:
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
            if x == bank_in: condition_node = bank_in_node
            elif x == bank_out: condition_node = bank_out_node
            cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[2]}",f"{condition_node}.firstTerm")
            cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[2]}",f"{condition_node}.colorIfTrueR")

            math_node = cmds.shadingNode("floatMath",au=1,n=f"math_{x}")

            cmds.connectAttr(f"{condition_node}.outColorR",f"{math_node}.floatA")
            cmds.connectAttr(f"{math_node}.outFloat",f"{x}.rotateX")

            cmds.setAttr(f"{math_node}.operation",2)
            cmds.setAttr(f"{math_node}.floatB",2.5)

        cmds.setAttr(f"{bank_in_node}.operation",2)
        cmds.setAttr(f"{bank_out_node}.operation",4)

        # HEEL & TOE TWIST
        heel_jnt = f"jnt{self.reverse_foot_data['loc_heel'][3:]}"
        toe_jnt = f"jnt{self.reverse_foot_data['loc_toe'][3:]}"
        for x in [heel_jnt, toe_jnt]:
            math_node = cmds.shadingNode("floatMath",au=1,n=f"math_{x}")

            cmds.connectAttr(f"{math_node}.outFloat",f"{x}.rotateZ")

            cmds.setAttr(f"{math_node}.operation",2)
            cmds.setAttr(f"{math_node}.floatB",2.5)

            if x == heel_jnt:
                cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[3]}",f"{math_node}.floatA")
            if x == toe_jnt:
                cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[4]}",f"{math_node}.floatA")

        # ROLL
        ball_jnt = f"jnt{self.reverse_foot_data['loc_ball'][3:]}"
        condition_node = self.create_condition_node(f"cond_{ball_jnt}")
        zeroed_math_node = cmds.shadingNode("floatMath",au=1,n=f"math_zeroed_{ball_jnt}")
        reversed_math_node = cmds.shadingNode("floatMath",au=1,n=f"math_reversed_{ball_jnt}")
        roll_toe_math_node = cmds.shadingNode("floatMath",au=1,n=f"math_roll_{toe_jnt}")
        roll_heel_math_node = cmds.shadingNode("floatMath",au=1,n=f"math_roll_{heel_jnt}")
        roll_toe_condition_node = self.create_condition_node(f"cond_roll_{toe_jnt}")
        roll_heel_condition_node = self.create_condition_node(f"cond_heel_{heel_jnt}")

        cmds.connectAttr(f"{zeroed_math_node}.outFloat",f"{condition_node}.colorIfTrueR")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"{condition_node}.firstTerm")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"{roll_toe_condition_node}.firstTerm")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"{roll_heel_condition_node}.firstTerm")
        cmds.connectAttr(f"{condition_node}.outColorR",f"{reversed_math_node}.floatA")
        cmds.connectAttr(f"{roll_toe_math_node}.outFloat",f"{roll_toe_condition_node}.colorIfTrueR")
        cmds.connectAttr(f"{roll_heel_math_node}.outFloat",f"{roll_heel_condition_node}.colorIfTrueR")

        cmds.connectAttr(f"{roll_toe_condition_node}.outColorR",f"{toe_jnt}.rotateY")
        cmds.connectAttr(f"{roll_heel_condition_node}.outColorR",f"{heel_jnt}.rotateY")
        cmds.connectAttr(f"{reversed_math_node}.outFloat",f"{ball_jnt}.rotateY")

        cmds.setAttr(f"{roll_toe_math_node}.operation",2)
        cmds.setAttr(f"{roll_toe_math_node}.floatB",4.5)
        cmds.setAttr(f"{roll_heel_math_node}.operation",2)
        cmds.setAttr(f"{roll_heel_math_node}.floatB",2.5)
        cmds.setAttr(f"{zeroed_math_node}.operation",1)
        cmds.setAttr(f"{zeroed_math_node}.floatB",10)
        cmds.setAttr(f"{reversed_math_node}.operation",2)
        cmds.setAttr(f"{reversed_math_node}.floatB",-2.5)
        cmds.setAttr(f"{condition_node}.operation",3)
        cmds.setAttr(f"{condition_node}.secondTerm",10)
        cmds.setAttr(f"{roll_toe_condition_node}.operation",2)
        cmds.setAttr(f"{roll_heel_condition_node}.operation",4)

        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"{roll_toe_math_node}.floatA")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"{roll_heel_math_node}.floatA")
        cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[1]}",f"{zeroed_math_node}.floatA")

    def create_system(self):
        side = self.side()
        parent_order = [self.reverse_foot_data["loc_heel"],
                        self.reverse_foot_data["loc_toe"],
                        self.reverse_foot_data["bank_in"],
                        self.reverse_foot_data["bank_out"],
                        self.reverse_foot_data["loc_ball"],
                        self.reverse_foot_data["loc_ankle"]]
        parent_order.reverse()

        for loc in range(len(parent_order)):
            try:
                cmds.parent(parent_order[loc],parent_order[loc+1])
            except:
                pass

        rev_list = self.create_rev_jnts()
        jnt_verification_values = [self.module.rev_locators["ankle"],self.module.rev_locators["ball"],self.module.rev_locators["toe"]]
        jnt_list = [item for item in self.system["ik_joint_list"] if any(key in item for key in jnt_verification_values)]

        self.foot_ctrl = [x for x in self.system["ik_ctrl_list"] if cmds.attributeQuery("handle", node=x, exists=True) and cmds.getAttr(f"{x}.handle", asString=1) == "True"][0]
        self.foot_attr()

        hdl_rev_ball = cmds.ikHandle(n=f"hdl_rev_ball{side}_#",sj=jnt_list[0],ee=jnt_list[1],sol="ikSCsolver")[0]
        cmds.parent(hdl_rev_ball,rev_list[2])
        hdl_rev_toe = cmds.ikHandle(n=f"hdl_rev_toe{side}_#",sj=jnt_list[1],ee=jnt_list[2],sol="ikSCsolver")[0]
        cmds.parent(hdl_rev_toe,rev_list[1])

        cmds.parent(rev_list[0],self.reverse_foot_data["loc_ankle"])

        cmds.parentConstraint(self.foot_ctrl,self.reverse_foot_data["loc_heel"],mo=1,n=f"pConst_{self.reverse_foot_data['loc_heel']}")
        if cmds.listRelatives(self.system["ik_handle"],c=1, type="parentConstraint"):
            cmds.delete(cmds.listRelatives(self.system["ik_handle"],c=1, type="parentConstraint"))
            cmds.parentConstraint(f"jnt{self.reverse_foot_data['loc_ankle'][3:]}",self.system["ik_handle"][0],
                                  mo=1,n=f"pConst_{self.system['ik_handle'][0]}")

        cmds.parent(self.reverse_foot_data["loc_heel"],f"grp_ik_ctrls_{self.system['master_guide']}")
        cmds.setAttr(f"{self.reverse_foot_data['loc_heel']}.overrideEnabled",1)

    def collect_rev_foot(self):
        return self.reverse_foot_data["loc_heel"]
