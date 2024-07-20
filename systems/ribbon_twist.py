import maya.cmds as cmds
import importlib
from systems.utils import OPM
importlib.reload(OPM)


class ribbon_twist():
    def __init__(self):
        selected_surface = cmds.ls(selection=True)
        if selected_surface:
            self.nurbs_surface = selected_surface[0]
            self.grp = f"grp_{self.nurbs_surface}"
            self.grp_list = cmds.listRelatives(self.grp, c=1)
            self.skin_object_list = []
            self.duplicate_ctrl_joints()
            self.create_tween_controls()

            iso_list = self.select_isoparms(UV="U")
            self.insert_offset_isoparms(iso_list)
            self.skin_ribbon()

            cmds.select(clear=1)
        else:
            print("Please select a NURBS surface.")

    def select_isoparms(self, UV):
        surface_info = cmds.createNode('surfaceInfo')

        cmds.connectAttr(f"{self.nurbs_surface}.worldSpace[0]", f"{surface_info}.inputSurface", f=True)

        iso_list = cmds.getAttr(f"{surface_info}.knots{UV}")[0]
        iso_list = list(dict.fromkeys(iso_list))
        print(f"iso_list: {iso_list}")
        cmds.delete(surface_info)
        return iso_list

    def insert_offset_isoparms(self, iso_list):
        offset = 0.01
        fol_jnt_grp = [cmds.listRelatives(x,c=1) for x in self.grp_list if "_fol" in x][0]
        iso_jnts_len = []
        iso_jnts_len = [fol for fol in range(len(fol_jnt_grp)) for x in self.ctrl_jnt_grp if f"jnt_ctrl_{fol_jnt_grp[fol]}" == x]

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
            cmds.insertKnotSurface(self.nurbs_surface, d=1, p=param_value_plus, rpo=1)
            cmds.insertKnotSurface(self.nurbs_surface, d=1, p=param_value_minus, rpo=1)
            cmds.delete(self.nurbs_surface, constructionHistory=True)

    def duplicate_ctrl_joints(self):
        self.ctrl_jnt_grp = [cmds.listRelatives(x, c=1) for x in self.grp_list if "skn_jnt" in x][0]
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
        self.ctrl_jnt_prnt_grp = [x for x in self.grp_list if "skn_jnt" in x][0]
        fol_jnts = [cmds.listRelatives(i, ad=1, type="joint")[0] for x in self.grp_list if "fol" in x for i in cmds.listRelatives(x, c=1)]
        filtered_fol_jnts = fol_jnts
        all_fol_jnts = [cmds.listRelatives(i, ad=1, type="joint")[0] for x in self.grp_list if "fol" in x for i in cmds.listRelatives(x, c=1)]
        filtered_fol_jnts = [x.replace("_ctrl_", "_fol_") for x in self.ctrl_jnt_grp if x.replace("_ctrl_", "_fol_") in fol_jnts]

        for tmp in filtered_fol_jnts:
            fol_jnts.remove(tmp)

        for x in fol_jnts:
            tween_ctrl = x.replace("_fol_","_tween_")
            cmds.duplicate(x,n=tween_ctrl,parentOnly=1)
            offset_grp = cmds.group(n=f"{x}_offset",em=1)
            aim_grp = cmds.group(n=f"{x}_aim",p=f"{x}_offset",em=1)
            cmds.matchTransform(f"{x}_offset", tween_ctrl)
            cmds.parent(tween_ctrl,self.ctrl_jnt_prnt_grp)

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
