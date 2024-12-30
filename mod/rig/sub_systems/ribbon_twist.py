import maya.cmds as cmds
import importlib
from mod.rig.utils import OPM, utils
from mod.rig.systems import ribbon

importlib.reload(OPM)
importlib.reload(utils)
importlib.reload(ribbon)


class prep_skeleton():
    def __init__(self,key,system):
        self.key = key
        module = importlib.import_module(f"mod.modules.{self.key['module']}")
        importlib.reload(module)
        for guide in self.key["guide_list"]:
            rig_joint = f"jnt_{system}_{guide}"
            if module.twist_joint["start"] in rig_joint:
                start_joint = rig_joint
            elif module.twist_joint["end"] in rig_joint:
                end_joint = rig_joint

        self.joint_list = utils.get_joints_between(start_joint, end_joint)
        self.create_tween_joints()

        if system == "rig":
            points_to_create_on = utils.get_joints_between(start_joint, end_joint)
            self.ribbon_module = ribbon.create_ribbon(self.key, self.key["module"],ctrl_amount=len(self.joint_list), ribbon_type="ribbon_twist",start_joint=start_joint, end_joint=end_joint, joint_list=points_to_create_on)

    def create_tween_joints(self):
        for x in range(len(self.joint_list)):
            try:
                joint1 = self.joint_list[x]
                joint2 = self.joint_list[x+1]
                num_joints = cmds.getAttr(f"{self.key['master_guide']}.{self.key['master_guide']}_twist_amount")
                num_joints = int(num_joints)
                self.tween_joint_list = self.insert_joints_between(joint1, joint2, num_joints)
            except IndexError:
                pass

    def insert_joints_between(self, joint1, joint2, num_joints):
        if num_joints <= 0:
            return
        tween_joint_list = []

        # Get the positions of the existing joints
        pos1 = cmds.xform(joint1, q=True, ws=True, t=True)
        pos2 = cmds.xform(joint2, q=True, ws=True, t=True)

        # Calculate the step increment for each joint
        step = [(pos2[0] - pos1[0]) / (num_joints + 1),
                (pos2[1] - pos1[1]) / (num_joints + 1),
                (pos2[2] - pos1[2]) / (num_joints + 1)]

        # Create and position the new joints
        previous_joint = joint1
        for i in range(1, num_joints + 1):
            new_position = [pos1[0] + step[0] * i,
                            pos1[1] + step[1] * i,
                            pos1[2] + step[2] * i]
            joint1_split = joint1.split("_")
            joint1_split.insert(2, f"tween{i}")
            joint_name = '_'.join(joint1_split)
            new_joint = cmds.joint(p=new_position,n=joint_name)
            if i == 1:
                first_joint = new_joint
            tween_joint_list.append(new_joint)
            previous_joint = new_joint

        # Reparent the final joint to joint2
        cmds.parent(joint2, previous_joint)
        cmds.parent(first_joint, joint1)

        cmds.joint(first_joint, edit=True, zso=1, oj="xyz", sao="xup", ch=True)
        return tween_joint_list

    def return_data(self):
        return self.ribbon_module.get_ribbon_twist_data()


class ribbon_twist():
    def __init__(self,systems_to_be_made):
        for key in systems_to_be_made.values():
            if "twist_dict" in key.keys():
                twist_dict = key["twist_dict"]
                self.nurbs_surface = twist_dict["nurbs_curve"]
                self.grp = twist_dict["top_level_grp"]
                self.grp_skn_jnt = twist_dict["grp_skn_jnt"]
                self.grp_fol = twist_dict["grp_fol"]
                self.skin_object_list = []
                self.duplicate_ctrl_joints()
                self.create_tween_controls()

                iso_list = self.select_isoparms(UV="V")
                self.insert_offset_isoparms(iso_list)
                self.skin_ribbon()

            cmds.select(clear=1)

    def select_isoparms(self, UV):
        surface_info = cmds.createNode('surfaceInfo')

        cmds.connectAttr(f"{self.nurbs_surface}.worldSpace[0]", f"{surface_info}.inputSurface", f=True)

        iso_list = cmds.getAttr(f"{surface_info}.knots{UV}")[0]
        iso_list = list(dict.fromkeys(iso_list))
        cmds.delete(surface_info)
        return iso_list

    def insert_offset_isoparms(self, iso_list):
        offset = 0.05
        fol_jnt_grp = cmds.listRelatives(self.grp_fol,c=1)
        ctrl_jnt_grp = cmds.listRelatives(self.grp_skn_jnt,c=1)
        iso_jnts_len = []
        iso_jnts_len = [fol for fol in range(len(fol_jnt_grp)) for x in ctrl_jnt_grp if f"jnt_ctrl{fol_jnt_grp[fol][3:]}" == x]

        filtered_iso_list = []
        for x in range(len(iso_list)):
            if x in iso_jnts_len:
                filtered_iso_list.append(iso_list[x])
        # filtered_iso_list = [filtered_iso_list.append(iso_list[x]) for x in range(len(iso_list)) if x in iso_jnts_len]

        for iso in filtered_iso_list:
            # Calculate the new parameter values
            param_value_plus = iso + offset
            param_value_minus = iso - offset

            # Insert the isoparms
            cmds.insertKnotSurface(self.nurbs_surface, d=0, p=param_value_plus, rpo=1)
            cmds.insertKnotSurface(self.nurbs_surface, d=0, p=param_value_minus, rpo=1)
            cmds.delete(self.nurbs_surface, constructionHistory=True)

    def duplicate_ctrl_joints(self):
        self.ctrl_jnt_grp = cmds.listRelatives(self.grp_skn_jnt, c=1)
        for x in range(len(self.ctrl_jnt_grp)):
            current = self.ctrl_jnt_grp[x]
            try: next = self.ctrl_jnt_grp[x+1]
            except IndexError: next = None
            try: previous = self.ctrl_jnt_grp[x-1]
            except IndexError: previous = None
            # print(f"Current: {current}, next: {next}, previous: {previous}")

            if next is None:
                pass
            else:
                # angle jnt
                angle_name = self.ctrl_jnt_grp[x].replace("_ctrl_","_angle_")
                cmds.duplicate(current,n=angle_name,parentOnly=1)
                cmds.parent(angle_name,current)

                # angle tip jnt
                angle_tip_name = angle_name.replace("_angle_","_angletip_")
                cmds.duplicate(angle_name,n=angle_tip_name,parentOnly=1)
                cmds.parent(angle_tip_name,angle_name)
                cmds.matchTransform(angle_tip_name, next,rot=False,scale=False)
                radius = cmds.getAttr(f"{angle_tip_name}.radius")
                cmds.setAttr(f"{angle_tip_name}.radius",radius-0.5)

                hdl_name = next.replace("_ctrl_","_hdl_")
                cmds.ikHandle(sj=angle_name, ee=angle_tip_name,solver="ikSCsolver",n=hdl_name)
                cmds.connectAttr(f"{next}.translate",f"{hdl_name}.translate")

                self.skin_object_list.append(angle_name)
        self.skin_object_list.extend(self.ctrl_jnt_grp)

    def create_tween_controls(self):
        # self.ctrl_jnt_prnt_grp = [x for x in self.grp_list if "skn_jnt" in x][0]
        fol_jnts = [cmds.listRelatives(i, ad=1, type="joint")[0] for x in self.grp if "fol" in x for i in cmds.listRelatives(x, c=1)]
        filtered_fol_jnts = fol_jnts
        all_fol_jnts = [cmds.listRelatives(i, ad=1, type="joint")[0] for x in self.grp if "fol" in x for i in cmds.listRelatives(x, c=1)]
        filtered_fol_jnts = [x.replace("_ctrl_", "_fol_") for x in self.ctrl_jnt_grp if x.replace("_ctrl_", "_fol_") in fol_jnts]

        for tmp in filtered_fol_jnts:
            fol_jnts.remove(tmp)

        for x in fol_jnts:
            tween_ctrl = x.replace("_fol_","_tween_")
            cmds.duplicate(x,n=tween_ctrl,parentOnly=1)
            offset_grp = cmds.group(n=f"{x}_offset",em=1)
            aim_grp = cmds.group(n=f"{x}_aim",p=f"{x}_offset",em=1)
            cmds.matchTransform(f"{x}_offset", tween_ctrl)
            cmds.parent(tween_ctrl,self.grp_skn_jnt)

            ctrl_crv = cmds.curve(p=[(0, 1, 1),(0, 1, -1),(0, -1, -1),(0, -1, 1),(0, 1, 1)],degree=1,n=f"ctrl{tween_ctrl[3:]}")
            cmds.matchTransform(ctrl_crv, tween_ctrl)
            cmds.parent(ctrl_crv, aim_grp)
            cmds.xform(ctrl_crv,s=[5,5,5])
            OPM.offsetParentMatrix(ctrl_crv)
            cmds.parentConstraint(ctrl_crv, tween_ctrl,mo=1,n=f"pConst_{ctrl_crv}")

            self.skin_object_list.append(tween_ctrl)

        for x in range(len(all_fol_jnts)):
            current = all_fol_jnts[x]
            try: next = all_fol_jnts[x+1]
            except IndexError: next = None
            try: previous = all_fol_jnts[x-1]
            except IndexError: previous = None

            if next and previous and current in fol_jnts:
                tmp = next.replace("_fol_","_")
                next = f"ctrl{tmp[3:]}"
                tmp = previous.replace("_fol_","_")
                previous = f"ctrl{tmp[3:]}"
                target = [next, previous]
                cmds.pointConstraint(target, f"{current}_offset",mo=0,n=f"pConst_{current}_offset")

            if previous and current in fol_jnts:
                previous = next.replace("_fol_","_ctrl_")
                cmds.aimConstraint(previous, f"{current}_aim",aimVector=(1,0,0),upVector=(1,0,0),worldUpType="objectrotation",worldUpVector=(0,1,0),worldUpObject=previous)

    def skin_ribbon(self):
        existing_skin_cluster = cmds.ls(cmds.listHistory(self.nurbs_surface), type="skinCluster")
        print(f"exsiting skin_cluster: {existing_skin_cluster}")
        if existing_skin_cluster:
            for obj in self.skin_object_list:
                cmds.skinCluster(existing_skin_cluster,edit=True,ps=0,ns=10,ai=obj)
        else:
            # Select joints and surface
            cmds.select(self.skin_object_list, self.nurbs_surface)

            # Create a skin cluster to bind the joints to the surface
            cmds.skinCluster(tsb=True)
            # cmds.skinCluster(self.existing_skin_cluster,edit=True,dr=4,ps=0,ns=10,ai=angle_name)
