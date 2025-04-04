import maya.cmds as cmds
import maya.api.OpenMaya as om
import importlib
from mod.rig.utils import OPM
importlib.reload(OPM)


class CreateReverseLocators():
    def __init__(self, guides,accessed_module):
        self.guides = guides
        self.grp_list = []
        self.accessed_module = accessed_module
        self.module = importlib.import_module(f"mod.modules.{accessed_module}")
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
        loc_prefix = "rev"

        if f"{rev_locators['ankle']}{side}" in cmds.ls(f"{rev_locators['ankle']}{side}"):
            cmds.error("ERROR: Item with the same name already exists.")

        # loc_name = [f"rev_{rev_locators['toe']}{side}",f"rev_{rev_locators['ball']}{side}",f"rev_{rev_locators['ankle']}{side}"]
        locators_keys = rev_locators.values()
        guide_name = [item for item in self.guides["ui_guide_list"] if any(key in item for key in locators_keys)]
        loc_name = [f"rev_{item}" for item in self.guides["ui_guide_list"] if any(key in item for key in locators_keys)]
        
        # list order needs to be: toe, ball, ankle
        loc_toe = loc_name[0]
        loc_ball = loc_name[1]
        loc_ankle = loc_name[2]
        offset = 7
        bank_in = f"rev_{side}_{rev_locators['bank_in']}_#"
        bank_out = f"rev_{side}_{rev_locators['bank_out']}_#"
        ball_guide = [guide for guide in self.guides["ui_guide_list"] if rev_locators["ball"] in guide][0]
        ankle_guide = [guide for guide in self.guides["ui_guide_list"] if self.module.rev_locators["ankle"] in guide][0]

        parent_grp = cmds.group(n=f"grp_rev_{ankle_guide}", w=True, em=True)
        cmds.matchTransform(parent_grp, ankle_guide, pos=True, rot=False, scale=False)
        cmds.matchTransform(parent_grp, ball_guide, pos=False, rx=False, ry=True, rz=False, scale=False)

        for x in range(len(loc_name)):
            try:
                loc = cmds.spaceLocator(n=loc_name[x])[0]
                cmds.matchTransform(loc,guide_name[x], rotation=False)
                self.follow(locator=loc, guide=loc_name[x].replace("rev_",""))
            except:
                cmds.error("Error: jnt_name cant be found check backend.")

        for x in [bank_in,bank_out]:
            tmp = cmds.spaceLocator(n=f"{x}")[0]
            #self.decompose_matrix(input=ball_guide ,output=tmp)
            cmds.matchTransform(tmp, loc_ball, pos=True, rot=False)
            cmds.matchTransform(tmp, loc_ball, pos=False, ry=True, rx=False, rz=False)
            if x == bank_in: bank_in = tmp
            elif x == bank_out: bank_out = tmp

        if "L" in bank_out and "L" in bank_in:
            cmds.matchTransform(bank_in,loc_toe, py=True, rot=False)
            cmds.matchTransform(bank_out,loc_toe, py=True, rot=False)
            # cmds.move(0,0,offset,bank_out,a=1, r=0)
            # cmds.move(0,0,-offset,bank_in,a=1, r=0)
            OPM.offsetParentMatrix(ctrl=[bank_in, bank_out])
            cmds.setAttr(f"{bank_out}.translateZ", offset)
            cmds.setAttr(f"{bank_in}.translateZ", -offset)
        elif "R" in bank_out and "R" in bank_in:
            cmds.matchTransform(bank_in,loc_toe, py=True, rot=False)
            cmds.matchTransform(bank_out,loc_toe, py=True, rot=False)
            OPM.offsetParentMatrix(ctrl=[bank_in, bank_out])
            cmds.setAttr(f"{bank_out}.translateZ", -offset)
            cmds.setAttr(f"{bank_in}.translateZ", offset)
        else:
            cmds.error("reverse_foot: No matching side suffex")

        for bank in [bank_in, bank_out]:
            self.follow(locator=bank, guide=ball_guide)

        loc_heel = cmds.spaceLocator(n=f"{loc_prefix}_{side}_{rev_locators['heel']}_#")[0]
        cmds.matchTransform(loc_heel,loc_ball, pos=True, rot=False)
        cmds.matchTransform(loc_heel, loc_ankle, pz=True, rot=False)
        cmds.matchTransform(loc_heel,loc_toe, py=True, rot=False)
        self.follow(locator=loc_heel, guide=ball_guide)

        loc_list = [loc_heel,loc_toe,loc_ball,loc_ankle,bank_in, bank_out]


        cmds.parent(self.grp_list, parent_grp)

        return loc_list

    def get_locators(self):
        return self.locator_list

    def follow(self, locator=None, guide=None):
        grp = cmds.group(n=f"{locator}_follow", w=True, em=True)
        cmds.matchTransform(grp, guide, pos=True, rot=True, scale=False)
        constraint = cmds.parentConstraint(guide, grp, n=f"pConst_{grp}", mo=True)[0]
        cmds.parent(locator, grp)
        cmds.setAttr(f"{constraint}.hiddenInOutliner", True)
        self.grp_list.append(grp)

class CreateReverseFootQuadruped():
    def __init__(self, accessed_module, system):
        self.accessed_module = accessed_module
        self.module = importlib.import_module(f"mod.modules.{self.accessed_module}")
        importlib.reload(self.module)
        self.system = system
        self.tmp_locator_list = []
        for locator in self.system["rev_locators"]:
            loc = cmds.spaceLocator(n=f"loc_{locator}")[0]
            cmds.matchTransform(loc, locator)
            self.tmp_locator_list.append(loc)

        self.reverse_foot_data = {
            "loc_heel": self.tmp_locator_list[0],
            "loc_toe": self.tmp_locator_list[1],
            "loc_ball": self.tmp_locator_list[2],
            "loc_ankle": self.tmp_locator_list[3],
            "bank_in": self.tmp_locator_list[4],
            "bank_out": self.tmp_locator_list[5],
        }

        self.create_system()
        self.lock_attr(obj=f"ctrl_{self.reverse_foot_data['bank_in']}", attr_list=["tx","ty","tz","rx","ry","sx","sy","sz"])
        self.lock_attr(obj=f"ctrl_{self.reverse_foot_data['bank_out']}", attr_list=["tx","ty","tz","rx","ry","sx","sy","sz"])
        self.lock_attr(obj=f"ctrl_{self.reverse_foot_data['loc_heel']}", attr_list=["tx","ty","tz","rx","rz","sx","sy","sz"])
        self.lock_attr(obj=f"ctrl_{self.reverse_foot_data['loc_toe']}", attr_list=["tx","ty","tz","sx","sy","sz"])
        cmds.hide(self.reverse_foot_data["loc_heel"])

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

    def create_rev_controls(self):
        self.grp_list = []

        ball_child = cmds.listRelatives(f"{self.jnt_list[1]}_driver", c=True, type="parentConstraint")
        if ball_child: cmds.delete(ball_child)
        toe_child = cmds.listRelatives(f"{self.jnt_list[2]}_driver", c=True, type="parentConstraint")
        if toe_child: cmds.delete(toe_child)
        ankle_child = cmds.listRelatives(f"{self.jnt_list[0]}_driver", c=True, type="parentConstraint")

        cmds.makeIdentity(f"{self.jnt_list[1]}_driver", apply=True, t=False, r=True, s=False)
        cmds.makeIdentity(f"{self.jnt_list[2]}_driver", apply=True, t=False, r=True, s=False)

        for rev_loc in self.reverse_foot_data.keys():
            ctrl = cmds.circle(n=f"ctrl_{self.reverse_foot_data[rev_loc]}", nr=(0,1,0))[0]
            cmds.matchTransform(ctrl, self.reverse_foot_data[rev_loc])
            grp = cmds.group(n=f"offset_{self.reverse_foot_data[rev_loc]}", em=True)
            self.grp_list.append(grp)
            cmds.matchTransform(grp, self.reverse_foot_data[rev_loc])
            cmds.parent(ctrl, grp)
            OPM.offsetParentMatrix(ctrl=[ctrl, self.reverse_foot_data[rev_loc]])
            if "bank" in self.reverse_foot_data[rev_loc]:
                cmds.parentConstraint(self.foot_ctrl, grp, mo=True)
                connection_object = self.reverse_foot_data[rev_loc]
            elif "ball" in rev_loc:
                cmds.parentConstraint(f"jnt{self.reverse_foot_data[rev_loc][3:]}", grp, mo=True)
                connection_object = f"jnt{self.reverse_foot_data[rev_loc][3:]}"
            else:
                cmds.parentConstraint(self.reverse_foot_data[rev_loc], grp, mo=True)
                connection_object = f"jnt{self.reverse_foot_data[rev_loc][3:]}"
            
            if "heel" in rev_loc:
                cmds.connectAttr(f"{ctrl}.rotateX", f"{connection_object}.rotateY")
                cmds.connectAttr(f"{ctrl}.rotateY", f"{connection_object}.rotateZ")
                cmds.connectAttr(f"{ctrl}.rotateZ", f"{connection_object}.rotateX")
            else:
                for axis in ["X","Y","Z"]:
                    cmds.connectAttr(f"{ctrl}.rotate{axis}", f"{connection_object}.rotate{axis}")

        multi_node_1 = cmds.createNode("multiplyDivide", n=f"{self.reverse_foot_data['loc_toe']}_revfoot_multi", ss=True)
        cmds.connectAttr(f"ctrl_{self.reverse_foot_data['loc_toe']}.rotateX", f"{multi_node_1}.input1X", force=True)
        cmds.connectAttr(f"ctrl_{self.reverse_foot_data['loc_toe']}.rotateZ", f"{multi_node_1}.input1Z", force=True)
        cmds.connectAttr(f"{multi_node_1}.outputX", f"jnt{self.reverse_foot_data['loc_toe'][3:]}.rotateX", force=True)
        cmds.connectAttr(f"{multi_node_1}.outputZ", f"jnt{self.reverse_foot_data['loc_toe'][3:]}.rotateZ", force=True)
        
        multi_node_2 = cmds.createNode("multiplyDivide", n=f"{self.reverse_foot_data['loc_ball']}_revfoot_multi", ss=True)
        cmds.connectAttr(f"ctrl_{self.reverse_foot_data['loc_toe']}.rotateY", f"{multi_node_2}.input1Y", force=True)
        cmds.connectAttr(f"{multi_node_2}.outputY", f"jnt{self.reverse_foot_data['loc_ball'][3:]}.rotateY", force=True)

        for xyz in ["X","Y","Z"]:
            cmds.setAttr(f"{multi_node_1}.input2{xyz}", -1)
            cmds.setAttr(f"{multi_node_2}.input2{xyz}", -1)

        # cmds.aimConstraint(f"jnt{self.reverse_foot_data['loc_ball'][3:]}",f"{self.jnt_list[0]}_driver", mo=False, aim=(1.0,0.0,0.0),u=(1.0,0.0,0.0),wu=(0.0,1.0,0.0))
        
        multi_node = cmds.createNode('multiplyDivide', name=f"multi_{self.reverse_foot_data['loc_ball']}_revfoot")
        cmds.connectAttr(f"jnt{self.reverse_foot_data['loc_ball'][3:]}.rotateY", f"{multi_node}.input1Y")
        cmds.connectAttr(f"{multi_node}.outputY", f"{self.jnt_list[1]}.rotateY")
        if cmds.getAttr(f"{self.system['master_guide']}.is_mirrored", asString=True) == "Yes":
            cmds.setAttr(f"{multi_node}.input2Y", 1)
        else:
            cmds.setAttr(f"{multi_node}.input2Y", -1)

        cmds.parentConstraint(self.jnt_list[2],f"{self.jnt_list[2]}_driver", mo=True)
        cmds.parentConstraint(self.jnt_list[1],f"{self.jnt_list[1]}_driver", mo=True)
        
        cmds.parentConstraint(f"jnt{self.reverse_foot_data['loc_ankle'][3:]}", self.jnt_list[0], n=f"pConst_{self.reverse_foot_data['loc_ankle']}", mo=True)
        cmds.parentConstraint(f"jnt{self.reverse_foot_data['loc_toe'][3:]}", self.jnt_list[2], n=f"pConst_{self.reverse_foot_data['loc_toe']}", mo=True)
        
        hock_group = self.hock_rotation()
        # cmds.parentConstraint(f"jnt{self.reverse_foot_data['loc_ankle'][3:]}", hock_group, n=f"pConst_{self.reverse_foot_data['loc_ankle']}", mo=True)

        cmds.hide(f"ctrl_{self.reverse_foot_data['loc_ankle']}")
        cmds.hide(f"ctrl_{self.reverse_foot_data['loc_ball']}")

    def hock_rotation(self):
        hock_ctrl = next((ctrl for ctrl in self.system['ik_ctrl_list'] if self.module.ik_joints['hock'] in ctrl), None)
        hock_group = cmds.group(hock_ctrl,n=f"offset_revfoot_{hock_ctrl}",p=cmds.listRelatives(hock_ctrl, p=True)[0])
        cmds.addAttr(hock_ctrl, ln=f"{self.system['master_guide']}_rev_divider", nn="Hock Rev Foot Orientation", at="enum", enumName="------------", k=True)
        cmds.setAttr(f"{hock_ctrl}.{self.system['master_guide']}_rev_divider", lock=True)

        const_tra = cmds.parentConstraint(
                f"jnt{self.reverse_foot_data['loc_ankle'][3:]}", 
                hock_group, 
                n=f"pConst_{self.reverse_foot_data['loc_ankle']}", 
                mo=True)[0]
        
        cmds.addAttr(hock_ctrl, ln=f"{self.system['master_guide']}_follow_rev", nn="Follow Rev", at="enum", enumName="Ignore:Follow",k=True)
        cmds.setAttr(f"{hock_ctrl}.{self.system['master_guide']}_follow_rev", 1)
        cmds.connectAttr(f"{hock_ctrl}.{self.system['master_guide']}_follow_rev",f"{const_tra}.jnt{self.reverse_foot_data['loc_ankle'][3:]}W0",f=True)

        return hock_group

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

        self.rev_list = self.create_rev_jnts()
        jnt_verification_values = [self.module.rev_locators["ankle"],self.module.rev_locators["ball"],self.module.rev_locators["toe"]]
        self.jnt_list = [item for item in self.system["ik_joint_list"] if any(key in item for key in jnt_verification_values)]

        self.foot_ctrl = [x for x in self.system["ik_ctrl_list"] if cmds.attributeQuery("reverse_parent", node=x, exists=True) and cmds.getAttr(f"{x}.reverse_parent", asString=1) == "True"][0]
        print(f"REVERSE FOOT: {self.foot_ctrl}")

        cmds.parent(self.rev_list[0],self.reverse_foot_data["loc_ankle"])
        
        self.create_rev_controls()

        cmds.parentConstraint(self.foot_ctrl,self.reverse_foot_data["loc_heel"],mo=1,n=f"pConst_{self.reverse_foot_data['loc_heel']}")
        if cmds.listRelatives(self.system["ik_handle"],c=1, type="parentConstraint"):
            cmds.delete(cmds.listRelatives(self.system["ik_handle"],c=1, type="parentConstraint"))
            cmds.parentConstraint(f"jnt{self.reverse_foot_data['loc_ankle'][3:]}",self.system["ik_handle"][0],
                                  mo=1,n=f"pConst_{self.system['ik_handle'][0]}")

        cmds.parent(self.reverse_foot_data["loc_heel"],f"grp_ik_ctrls_{self.system['master_guide']}")
        cmds.parent(self.grp_list, f"grp_ik_ctrls_{self.system['master_guide']}")
        cmds.setAttr(f"{self.reverse_foot_data['loc_heel']}.overrideEnabled",1)

    def lock_attr(self, obj=None, attr_list=[]):
        for attr in attr_list:
            cmds.setAttr(f"{obj}.{attr}", lock=True, keyable=False)

    def collect_rev_foot(self):
        return self.reverse_foot_data["loc_heel"]

class CreateReverseFootBiped():
    def __init__(self, accessed_module, system):
        self.attr_list = ["Rev_Foot_Dvdr","Roll","Bank","Heel_Twist","Toe_Twist"]
        self.module = importlib.import_module(f"mod.modules.{accessed_module}")
        importlib.reload(self.module)
        self.system = system
        self.tmp_locator_list = []
        for locator in self.system["rev_locators"]:
            loc = cmds.spaceLocator(n=f"loc_{locator}")[0]
            cmds.matchTransform(loc, locator)
            self.tmp_locator_list.append(loc)

        self.reverse_foot_data = {
            "loc_heel": self.tmp_locator_list[0],
            "loc_toe": self.tmp_locator_list[1],
            "loc_ball": self.tmp_locator_list[2],
            "loc_ankle": self.tmp_locator_list[3],
            "bank_in": self.tmp_locator_list[4],
            "bank_out": self.tmp_locator_list[5],
        }

        self.create_system()
        ik_toe = self.reverse_foot_data["loc_toe"].replace("loc_rev_","jnt_ik_")
        rev_toe = self.reverse_foot_data["loc_toe"].replace("loc_rev_","jnt_rev_")
        # cmds.pointConstraint(rev_toe, ik_toe,mo=False, n=f"pConst_{rev_toe}")

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
        OPM.offsetParentMatrix(ctrl=bank_in)
        OPM.offsetParentMatrix(ctrl=bank_out)

        # BANK IN OUT
        bank_in_node = self.create_condition_node(f"cond_{bank_in}")
        bank_out_node = self.create_condition_node(f"cond_{bank_out}")
        for x in [bank_in,bank_out]:
            if x == bank_in: condition_node = bank_in_node
            elif x == bank_out: condition_node = bank_out_node
            cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[2]}",f"{condition_node}.firstTerm")
            cmds.connectAttr(f"{self.foot_ctrl}.{self.attr_list[2]}",f"{condition_node}.colorIfTrueR")

            math_node = cmds.shadingNode("floatMath",au=1,n=f"math_{x}")
            reverse_node = cmds.createNode("multiplyDivide", n=f"reverse_{x}")

            cmds.connectAttr(f"{condition_node}.outColorR",f"{math_node}.floatA")
            cmds.connectAttr(f"{math_node}.outFloat",f"{reverse_node}.input1X")
            cmds.connectAttr(f"{reverse_node}.outputX",f"{x}.rotateX")

            cmds.setAttr(f"{math_node}.operation",2)
            cmds.setAttr(f"{math_node}.floatB",2.5)
            cmds.setAttr(f"{reverse_node}.input2X", -1)

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

        self.foot_ctrl = [x for x in self.system["ik_ctrl_list"] if cmds.attributeQuery("reverse_parent", node=x, exists=True) and cmds.getAttr(f"{x}.reverse_parent", asString=1) == "True"][0]
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
