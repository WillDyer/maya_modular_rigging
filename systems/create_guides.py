import maya.cmds as cmds
import importlib
import sys
import os
from systems.utils import (connect_modules, utils, reverse_foot)
importlib.reload(connect_modules)
importlib.reload(utils)
importlib.reload(reverse_foot)

scale = 1

class Guides():
    def __init__(self,accessed_module, offset,side, to_connect_to,use_existing_attr):
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        importlib.reload(self.module)
        if accessed_module == "hand":
            self.create_guide = self.guides_hand(accessed_module,offset,side,to_connect_to,use_existing_attr)
        else:
            self.create_guide = self.guides(accessed_module,offset,side,use_existing_attr)
        try: 
            self.module.reverse_foot
            reverse_foot.CreateReverseFoot(self.create_guide, accessed_module).create_loc()
            print("rev foot existssss")
        except AttributeError: pass

    def collect_guides(self):
        return self.create_guide

    def guides(self,accessed_module, offset,side,use_existing_attr):
        connector_list = []
        self.system_to_connect = []
        selection = cmds.ls(sl=1)
        if selection:
            if "master" in selection[0]:
                cmds.warning("Cant attach a new module to a master control please select a guide.")
            elif "master" not in selection[0]:
                guide = self.creation(accessed_module,offset,side,connector_list,use_existing_attr)
                master_guide = guide["master_guide"]
                connector = connect_modules.attach(master_guide, selection)
                connector_list.append(connector[1])
                self.system_to_connect = connect_modules.prep_attach_joints(master_guide, selection, need_child=True)
                guide.update({"system_to_connect": self.system_to_connect})
                return guide
        else:
            guide = self.creation(accessed_module,offset,side,connector_list,use_existing_attr)
            guide.update({"system_to_connect": []})
            return guide
        
    def guides_hand(self, accessed_module, offset,side, to_connect_to,use_existing_attr):
        connector_list = []
        if accessed_module == "hand":
            guide = self.creation(accessed_module,offset,side,connector_list,use_existing_attr)
            master_guide = guide["master_guide"]
            connector = connect_modules.attach(master_guide, to_connect_to)
            connector_list.append(connector[1])
            self.system_to_connect = connect_modules.prep_attach_joints(master_guide, to_connect_to, need_child=False)
            guide.update({"system_to_connect": self.system_to_connect})
            return guide


    def creation(self,accessed_module,offset,side,connector_list,use_existing_attr):
        ABC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),"imports","guide_shape.abc")
        COLOR_CONFIG = {'l': 6, 'r': 13, 'default': 22}
        guide_list = []
        root_exists = False

        if self.module.side == "None":
            side = ""
        else:
            side = self.module.side

        # create master guide for module
        if "root" in self.module.system:
            master_guide = "root"
        elif "proximal" in self.module.system:
            master_guide = "proximal"
        else:
            master_guide = utils.create_cube(f"master_{accessed_module}{side}_#",scale=[5,5,5])
            pos = self.module.system_pos[self.module.system[0]]
            rot = self.module.system_rot[self.module.system[0]]
            cmds.xform(master_guide,ws=1,t=[pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2]])
            cmds.xform(master_guide,ws=1,ro=[rot[0],rot[1],rot[2]])


        for x in self.module.system:
            # Import custom guide crv if fails use locator
            try:
                if "root" in x:
                    imported = cmds.circle(r=50,nr=[0,1,0])
                    root_exists = True
                    guide = cmds.rename(imported[0], f"{x}{side}")
                else:
                    imported = cmds.file(ABC_FILE, i=1,namespace="test",rnn=1)
                    cmds.scale(self.module.guide_scale,self.module.guide_scale, self.module.guide_scale, imported)
                    guide = cmds.rename(imported[0], f"{x}{side}_#")
                if "root" in x and root_exists == True:
                    master_guide = guide
                elif "proximal" in x:
                    master_guide = guide
                else:
                    guide_list.append(guide)
                for shape in imported[1:]:
                    shape = shape.split("|")[-1]
                    cmds.rename(shape, f"{guide}_shape_#")

                cmds.setAttr(f"{guide}.overrideEnabled",1)
                cmds.setAttr(f"{guide}.overrideColor",COLOR_CONFIG["default"])
            except RuntimeError:
                print("Couldnt load file using basic shapes instead")
                cmds.spaceLocator(n=x)

            # set location of guide crvs then OPM
            pos = self.module.system_pos[x]
            rot = self.module.system_rot[x]
            cmds.xform(guide,ws=1,t=[pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2]])
            cmds.xform(guide,ws=1,ro=[rot[0],rot[1],rot[2]])

        # parent together
        guide_list.reverse()
        ui_guide_list = guide_list
        guide_list.append(master_guide)
        for x in range(len(guide_list)):
            try:
                cmds.parent(guide_list[x],guide_list[x+1])
                connector = utils.connector(guide_list[x],guide_list[x+1])
                connector_list.append(connector)
            except:
                pass # end of list

        if "grp_connector_clusters" in cmds.ls("grp_connector_clusters"):
            cmds.parent(connector_list,"grp_connector_clusters")
        else:
            cmds.group(connector_list,n="grp_connector_clusters",w=1)

        self.available_rig_types = ":".join(self.module.available_rig_types)
        custom_attr = self.add_custom_attr(guide_list, master_guide, self.module,use_existing_attr)
        cmds.addAttr(master_guide, ln="is_master",at="enum",en="True",k=0) # adding master group attr
        cmds.addAttr(master_guide, ln="base_module",at="enum",en=accessed_module,k=0) # module attr
        cmds.addAttr(master_guide, ln="module_side",at="enum",en=side,k=0) # module side
        cmds.addAttr(master_guide, ln="master_guide",at="enum",en=master_guide,k=0) # master guide
        for item in ["is_master","base_module","module_side","master_guide"]:
            cmds.addAttr(guide_list[:-1],ln=f"{item}", proxy=f"{guide_list[-1]}.{item}")
            for guide in guide_list[:-1]:
                cmds.setAttr(f"{guide}.{item}",k=0)

        ui_dict = {
            "master_guide": master_guide,
            "connector_list": connector_list,
            "ui_guide_list": ui_guide_list
        }
        return ui_dict #[master_guide, connector_list, ui_guide_list]

    def add_custom_attr(self,system, master_guide, module,use_existing_attr):
        custom_attrs = {"module_dvdr": ["enum","------------","MODULE",True],
                        "skeleton_dvdr": ["enum","------------", "SKELETON",True],
                        "mirror_jnts": ["enum","Mirror Joints", "No:Yes",False],
                        "twist_jnts": ["enum","Twist Joints", "Yes:No",False],
                        "twist_amount": ["float","Twist Amount", "UPDATE",False],
                        "rig_dvdr": ["enum","------------","RIG",True],
                        "rig_type": ["enum","Rig Type",self.available_rig_types,False],
                        "squash_stretch": ["enum","Squash Stech","No:Yes",False]
                        }
        def add_new_attr():
            if custom_attrs[i][0] == "enum":
                cmds.addAttr(master_guide,k=1,ln=f"{system[-1]}_{i}",nn=custom_attrs[i][1],at="enum",en=custom_attrs[i][2])
            elif custom_attrs[i][0] == "float":
                cmds.addAttr(master_guide,k=1,ln=f"{system[-1]}_{i}",nn=custom_attrs[i][1],at="float",min=0)
            if custom_attrs[i][3] == True:
                cmds.setAttr(f"{master_guide}.{system[-1]}_{i}", l=1)

        def add_proxy(list,skip_attr,proxy_item,add_missing):
            if add_missing:
                for item in skip_attr:
                    cmds.addAttr(list,ln=f"{master_guide}_{item}", proxy=f"{proxy_item}.{proxy_item}_{item}")
            else:
                for item in custom_attrs:
                    if item in skip_attr:
                        pass
                    else:
                        cmds.addAttr(list,ln=f"{master_guide}_{item}", proxy=f"{proxy_item}.{proxy_item}_{item}")

        if use_existing_attr:
            skip_attr = ["rig_type"]
            add_proxy(system,skip_attr,proxy_item=use_existing_attr[0],add_missing=False)
            for i in skip_attr: add_new_attr()
            add_proxy(system[:-1],skip_attr,proxy_item=system[-1],add_missing=True)
        else:
            for i in custom_attrs: add_new_attr()
            add_proxy(system[:-1],skip_attr=[],proxy_item=system[-1],add_missing=False)