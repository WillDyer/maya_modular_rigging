import maya.cmds as cmds
from maya import OpenMayaUI as omui
import importlib

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance
import os.path
import sys
import subprocess

from systems import (
    joints,
    fk,
    ik,
    create_guides
)

from systems.utils import (
    connect_modules,
    utils,
    mirror_rig,
    ikfk_switch,
    system_group
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

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)

class QtSampler(QWidget):
    def __init__(self, *args, **kwargs): # __init__ is always the first thing to run when a class is made
        super(QtSampler,self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("AutoRigger")
        self.setFixedWidth(300)
        self.setFixedHeight(450)
        self.initUI()
        
        self.update_dropdown()
        self.module_created = 0
        self.created_guides = []
        self.systems_to_be_made = {}

        self.ui.image.setPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),"interface","UI_Logo.png"))
        self.ui.add_module.clicked.connect(self.add_module)
        self.ui.remove_module.clicked.connect(self.remove_module)
        self.ui.scale_box.valueChanged.connect(self.rig_global_scale)
        self.ui.create_skeleton.clicked.connect(self.create_joints)
        self.ui.edit_blueprint.clicked.connect(self.edit_blueprint)
        self.ui.polish_rig.clicked.connect(self.polish_rig)


    def initUI(self): # this loads the ui
        loader = QUiLoader()
        #UI_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/interface/WD_Rig_Builder.ui" # path to ui
        UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interface", "WD_Rig_Builder.ui")
        file = QFile(UI_FILE)
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, parentWidget=self)
        file.close()

    def rig_global_scale(self):
        global_scale = self.ui.scale_box.value()
        if "root" in cmds.ls("root"):
            for i in ["X","Y","Z"]:
                cmds.setAttr(F"root.scale{i}", global_scale)
        else:
            pass

    def update_dropdown(self):
        files = [".".join(f.split(".")[:-1]) for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))]
        try:
            files.remove("")
        except ValueError:
            pass
        files.remove("__init__")
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

        master_guide = create_guides.guides(module,offset,module_path.side)
        self.created_guides.append(master_guide)
        self.ui.skeleton_box.setEnabled(True)

        print(f"Module: {module}")
        print(f"Master Guide: {master_guide}")
        print(f"Created Guides: {self.created_guides}")

        temp_dict = {
            "module": module,
            "master_guide": master_guide,
            "joints": [],
            "side": module_path.side
        }
        self.systems_to_be_made[master_guide] = temp_dict
        cmds.select(clear=1)

    def remove_module(self):
        print("Run")
        module = cmds.ls(sl=1)
        for key in self.systems_to_be_made.values():
            print(key)
            print(key["master_guide"])
            if module[0] in key['master_guide']:
                self.systems_to_be_made.pop(module[0])

        print(self.systems_to_be_made)

    def create_joints(self):
        #orientation = self.ui.oritentation.currentText()

        jnt_list = joints.get_joint_list(self.ui.oritentation.currentText(),self.created_guides, system="rig")
        num = 0
        for dict in self.systems_to_be_made.values():
            dict["joints"] = jnt_list[num]
            num = num+1
        connect_modules.attach_joints()
        self.ui.polish_rig.setEnabled(True)

        mirror = mirror_rig.collect_mirror_data(self.systems_to_be_made)
        print("MIRROR RESULT")
        print(mirror)

        self.systems_to_be_made = mirror

    def edit_blueprint(self): #currently broke working for windows only.
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules")
        subprocess.Popen(f'explorer "{os.path.dirname(os.path.abspath(__file__))}/systems/modules/"')

    def polish_rig(self):
        
        for key in self.systems_to_be_made.values():
            master_guide = key['master_guide']
            rig_type = cmds.getAttr(f"{master_guide}.{master_guide}_rig_type")
            orientation = self.ui.oritentation.currentText()

            sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))
            module = importlib.import_module(key["module"])
            importlib.reload(module)
            print(f"systems_to_be_made: {key['joints']}")
            if rig_type == 0:
                fk_joint_list = joints.joint(orientation, master_guide, system="fk")
                fk.create_fk(fk_joint_list,delete_end=False)
                utils.constraint_from_lists_1to1(fk_joint_list, key["joints"],maintain_offset=1)
                print("fk")
            elif rig_type == 1:
                ik_joint_list = joints.joint(orientation, master_guide, system="ik")
                ik.create_ik(ik_joint_list, module.ik_joints)
                utils.constraint_from_lists_1to1(ik_joint_list, key["joints"],maintain_offset=1)
                print("ik")
            elif rig_type == 2:
                fk_joint_list = joints.joint(orientation, master_guide, system="fk")
                fk_module = fk.create_fk(fk_joint_list, delete_end=False)
                fk_ctrls = fk_module.get_ctrls()

                ik_joint_list = joints.joint(orientation, master_guide, system="ik")
                ik_module = ik.create_ik(ik_joint_list, module.ik_joints)
                ik_ctrls = ik_module.get_ctrls()

                utils.constraint_from_lists_2to1(ik_joint_list, fk_joint_list, key["joints"],maintain_offset=1)
                ikfk_switch.create_ikfk(key["joints"], fk_ctrls, ik_ctrls,ik_joint_list,fk_joint_list,master_guide)
                print("ikfk")
            else:
                cmds.error("ERROR: rig_type attribute cannot be found or attribute value cannot be found.")

        # delete guides CHANGE TO AFTER MADE SKELETON
        self.delete_guides()

        system_group.grpSetup()
        
        ctrl_list = cmds.ls("ctrl_*",type="transform")
        utils.colour_controls(ctrl_list)

    def delete_guides(self):
        for key in self.systems_to_be_made.values():
            cmds.delete(key["master_guide"])
        cmds.delete("grp_connector_clusters")

def main():
    ui = QtSampler()
    ui.show()
    return ui
