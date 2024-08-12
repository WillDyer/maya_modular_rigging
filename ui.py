import maya.cmds as cmds
from maya import OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance
import importlib
import os.path
import sys
import subprocess
import platform

from systems import (
    joints,
    fk,
    ik,
    create_guides,
    hands,
    ribbon,
    twist_joints
)

from systems.utils import (
    connect_modules,
    utils,
    mirror_rig,
    ikfk_switch,
    system_group,
    space_swap,
    reverse_foot
)

# debug
importlib.reload(joints)
importlib.reload(fk)
importlib.reload(ik)
importlib.reload(create_guides)
importlib.reload(connect_modules)
importlib.reload(utils)
importlib.reload(mirror_rig)
importlib.reload(ikfk_switch)
importlib.reload(system_group)
importlib.reload(space_swap)
importlib.reload(hands)
importlib.reload(reverse_foot)
importlib.reload(ribbon)
importlib.reload(twist_joints)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)


class QtSampler(QWidget):
    def __init__(self, *args, **kwargs):
        super(QtSampler,self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("AutoRigger")
        self.setFixedWidth(301)
        self.setFixedHeight(471)
        self.initUI()

        self.update_dropdown()
        self.module_created = 0
        self.created_guides = []
        self.systems_to_be_made = {}
        self.systems_rev_foot = {}
        self.systems_to_be_deleted_polished = []

        # page 1
        self.ui.image.setPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),"interface","UI_Logo.png"))
        self.ui.add_module.clicked.connect(self.add_module)
        self.ui.remove_module.clicked.connect(self.remove_module)
        self.ui.scale_box.valueChanged.connect(self.rig_global_scale)
        self.ui.create_skeleton.clicked.connect(self.create_joints)
        self.ui.edit_blueprint.clicked.connect(self.edit_blueprint)
        self.ui.polish_rig.clicked.connect(self.polish_rig)

        # page 2

        # page 3
        self.ui.colour_left.clicked.connect(lambda: self.colour_button(button="colour_left"))
        self.ui.colour_middle.clicked.connect(lambda: self.colour_button(button="colour_middle"))
        self.ui.colour_right.clicked.connect(lambda: self.colour_button(button="colour_right"))

    def initUI(self):
        loader = QUiLoader()
        UI_VERSION = "03"
        UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interface", f"WD_Rig_Builder_{UI_VERSION}.ui")
        print(f"UI file path: {UI_FILE}")  # Debug: Print the UI file path
        if not os.path.exists(UI_FILE):
            cmds.error(f"ERROR: UI file does not exist: {UI_FILE}")

        file = QFile(UI_FILE)
        if not file.open(QFile.ReadOnly):
            cmds.error(f"ERROR: Unable to open UI file: {UI_FILE}")

        self.ui = loader.load(file, parentWidget=self)
        file.close()

    def get_colour(self):
        colour = QColorDialog.getColor()
        if colour.isValid():
            red = colour.red()
            green = colour.green()
            blue = colour.blue()
            return {"red":red, "green":green, "blue":blue}
        else: return None

    def colour_button(self,button):
        colour = self.get_colour()
        button_name = getattr(self.ui, button)
        if colour: button_name.setStyleSheet(f"background-color: rgb({colour['red']}, {colour['green']}, {colour['blue']});")

    def rig_global_scale(self):
        global_scale = self.ui.scale_box.value()
        if "root" in cmds.ls("root"):
            for i in ["X","Y","Z"]:
                cmds.setAttr(F"root.scale{i}", global_scale)
        else:
            pass

    def update_dropdown(self):
        files = [".".join(f.split(".")[:-1]) for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))]
        try: files.remove("")
        except ValueError: pass
        files.remove("__init__")
        files.remove("hand")
        self.ui.available_modules.addItems(files)
        index = files.index("basic_root")
        self.ui.available_modules.setCurrentIndex(index)

    def add_module(self):
        module = self.ui.available_modules.currentText()
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))
        module_path = importlib.import_module(module)
        importlib.reload(module_path)
        offset = [
            self.ui.offset_x.value(),
            self.ui.offset_y.value(),
            self.ui.offset_z.value()
        ]

        guides = create_guides.Guides(module,offset,module_path.side,to_connect_to=[],use_existing_attr=[])
        guide = guides.collect_guides()
        if guide:
            master_guide = guide["master_guide"]
            guide_connector_list = guide["connector_list"]
            system_to_connect = guide["system_to_connect"]
            guide_list = guide["ui_guide_list"]
            if "rev_locators" in guide: rev_locators = guide["rev_locators"]
            else: rev_locators = []
            self.created_guides.append(master_guide)
            self.ui.skeleton_box.setEnabled(True)

            print(f"Module: {module}")
            print(f"Master Guide: {master_guide}")
            print(f"Created Guides: {self.created_guides}")

            temp_dict = {
                "module": module,
                "master_guide": master_guide,
                "guide_list": guide_list,
                "scale": module_path.guide_scale,
                "joints": [],
                "side": module_path.side,
                "connectors": guide_connector_list,
                "system_to_connect": system_to_connect,
                "space_swap": module_path.space_swapping,
                "ik_ctrl_list": [],
                "fk_ctrl_list": [],
                "ik_joint_list": [],
                "fk_joint_list": [],
                "rev_locators": rev_locators
            }
            self.systems_to_be_made[master_guide] = temp_dict

            if self.ui.add_hand.isChecked():
                hand_module = hands.create_hands(guide_list[0],self.systems_to_be_made, self.created_guides, self.ui.fingers_amount.value())
                self.systems_to_be_made = hand_module.get_dict()
                self.created_guides = hand_module.get_created_guides()
                self.ui.add_hand.setChecked(False)
                self.systems_to_be_deleted_polished.append(hand_module.get_hand_grp_to_delete())

        cmds.select(clear=1)

    def remove_module(self):
        module = cmds.ls(sl=1)
        for key in list(self.systems_to_be_made.values()):
            if module[0] in key['master_guide']:
                self.systems_to_be_made.pop(module[0])
                self.created_guides.remove(module[0])
                cmds.delete(module[0], key['connectors'])

    def create_joints(self):
        print(f"created_guides: {self.created_guides}")
        rig_jnt_list = joints.get_joint_list(self.ui.oritentation.currentText(),self.created_guides, system="rig")
        num = 0
        for dict in self.systems_to_be_made.values():
            dict["joints"] = rig_jnt_list[num]
            num = num+1
        self.ui.polish_rig.setEnabled(True)

        mirror_module = mirror_rig.mirror_data(self.systems_to_be_made, self.ui.oritentation.currentText())
        self.systems_to_be_made = mirror_module.get_mirror_data()

        skn_created_guides = [key["master_guide"] for key in self.systems_to_be_made.values()]
        print(skn_created_guides)
        skn_jnt_list = joints.get_joint_list(self.ui.oritentation.currentText(),skn_created_guides, system="skn")

        for key in self.systems_to_be_made.values():
            twist_joint = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_twist_jnts", asString=1)
            if twist_joint == "Yes":
                twist_amount = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_twist_amount")
                if twist_amount > 0:
                    rig_twist_instance = twist_joints.PrepSkeleton(self.ui.oritentation.currentText(),key,system="rig")
                    rig_twist_list = rig_twist_instance.return_data()
                    twist_joints.PrepSkeleton(self.ui.oritentation.currentText(),key,system="skn")
                    twist_joints.rig_to_skn(rig_twist_list)
                    key.update({"twist_dict": rig_twist_list})

        connect_modules.attach_joints(self.systems_to_be_made,system="rig")
        connect_modules.attach_joints(self.systems_to_be_made,system="skn")

        skn_jnt_list = [item for sublist in skn_jnt_list for item in sublist]
        for joint in skn_jnt_list: cmds.parentConstraint(f"jnt_rig{joint[7:]}",joint,mo=1,n=f"pConst_jnt_rig{joint[7:]}")

        self.hide_guides()
        cmds.select(cl=1)

        self.ui.skeleton_box.setEnabled(False)

    def edit_blueprint(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules")
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{path}"')
        elif platform.system() == "Linux":
            subprocess.Popen(['xdg-open', path])
        else: cmds.warning(f"OS not found or supported by this tool please use the following: Windows, Linux. Your current OS: {platform.system()}")

    def polish_rig(self):
        for key in self.systems_to_be_made.values():
            master_guide = key['master_guide']
            rig_type = cmds.getAttr(f"{master_guide}.{master_guide}_rig_type", asString=1)
            orientation = self.ui.oritentation.currentText()

            sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))
            module = importlib.import_module(key["module"])
            importlib.reload(module)
            if key["module"] == "basic_root": pass
            else:
                if rig_type == "FK":
                    fk_joint_list = joints.joint(orientation, master_guide, system="fk", )
                    fk_module = fk.create_fk(fk_joint_list,master_guide,key["scale"],delete_end=False)
                    fk_ctrls = fk_module.get_ctrls()
                    utils.constraint_from_lists_1to1(fk_joint_list, key["joints"],maintain_offset=1)
                    key.update({"fk_joint_list": fk_joint_list, "fk_ctrl_list": fk_ctrls})
                elif rig_type == "IK":
                    ik_joint_list = joints.joint(orientation, master_guide, system="ik")
                    ik_module = ik.create_ik(ik_joint_list,master_guide,module.ik_joints)
                    ik_ctrls = ik_module.get_ctrls()
                    ik_handle = ik_module.get_ik_hdl()
                    utils.constraint_from_lists_1to1(ik_joint_list, key["joints"],maintain_offset=1)
                    key.update({"ik_joint_list": ik_joint_list, "ik_ctrl_list": ik_ctrls, "ik_handle": ik_handle})
                elif rig_type == "IK_Ribbon":
                    ik_joint_list = joints.joint(orientation, master_guide, system="ik")
                    key.update({"ik_joint_list": ik_joint_list})
                    ik_module = ribbon.create_ribbon(key, key["module"],ctrl_amount=3, ribbon_type="ik_ribbon", start_joint="", end_joint="", joint_list="")
                    key.update({"ik_ctrl_list": ik_module.get_ribbon_ctrls()})
                    utils.constraint_from_lists_1to1(ik_joint_list, key["joints"],maintain_offset=1)
                elif rig_type == "FKIK":
                    fk_joint_list = joints.joint(orientation, master_guide, system="fk")
                    fk_module = fk.create_fk(fk_joint_list,master_guide,key["scale"],delete_end=False)
                    fk_ctrls = fk_module.get_ctrls()
                    key.update({"fk_joint_list": fk_joint_list, "fk_ctrl_list": fk_ctrls})

                    ik_joint_list = joints.joint(orientation, master_guide, system="ik")
                    ik_module = ik.create_ik(ik_joint_list,master_guide,module.ik_joints)
                    ik_ctrls = ik_module.get_ctrls()
                    ik_handle = ik_module.get_ik_hdl()
                    key.update({"ik_joint_list": ik_joint_list, "ik_ctrl_list": ik_ctrls, "ik_handle": ik_handle})

                    utils.constraint_from_lists_2to1(ik_joint_list, fk_joint_list, key["joints"],maintain_offset=1)
                    ikfk_switch.create_ikfk(key["joints"], fk_ctrls, ik_ctrls,ik_joint_list,fk_joint_list,master_guide)
                else:
                    cmds.error("ERROR: rig_type attribute cannot be found or attribute value cannot be found.")

                if rig_type == "FKIK" or rig_type == "IK":
                    try:
                        if key["rev_locators"]:
                            reverse_foot_module = reverse_foot.CreateReverseFoot(key["module"],key)
                    except KeyError:
                        print(f"Didnt find rev_locators in key not making reverse foot for: {key}")

        system_group.grpSetup(self.ui.rig_master_name.text())

        for key in self.systems_to_be_made.values():  # seperate loop to be sure systems are made before connecting
            rig_type = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_rig_type", asString=1)
            twist_joint = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_twist_jnts", asString=1)
            if key['system_to_connect']:
                systems_to_connect = key['system_to_connect']
                connect_modules.connect_polished(systems_to_connect)
            if rig_type == "FKIK":
                space_swap_module = space_swap.SpaceSwapping(key)

        self.delete_guides()

        button_names = ["colour_left","colour_middle","colour_right"]
        button_colour_dict = {"colour_left":[],"colour_middle":[],"colour_right":[]}
        for x in button_names:
            button_name = getattr(self.ui, x)
            palette = button_name.palette()
            button_colour = palette.color(button_name.backgroundRole())
            button_rgb = button_colour.getRgb()
            button_colour_dict[x] = list(button_rgb)
        button_colour_dict.update({"root": [0,255,0]})

        ctrl_list = cmds.ls("ctrl_*",type="transform")
        utils.colour_controls(ctrl_list,button_colour_dict)

        cmds.select(cl=1)

    def delete_guides(self):
        for key in self.systems_to_be_made.values():
            cmds.delete(key["master_guide"])
        cmds.delete("grp_connector_clusters")
        cmds.delete(self.systems_to_be_deleted_polished)

    def hide_guides(self):
        for key in self.systems_to_be_made.values():
            cmds.hide(key["master_guide"])
        cmds.hide("grp_connector_clusters")


def main():
    ui = QtSampler()
    ui.show()
    return ui
