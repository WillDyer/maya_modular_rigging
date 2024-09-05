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
    twist_joints,
    squash_and_stretch
)

from systems.utils import (
    connect_modules,
    utils,
    mirror_rig,
    ikfk_switch,
    system_group,
    space_swap,
    reverse_foot,
    guide_data
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
importlib.reload(squash_and_stretch)
importlib.reload(guide_data)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)


class QtSampler(QWidget):
    def __init__(self, *args, **kwargs):
        super(QtSampler,self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("AutoRigger")
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"interface","images","UI_Logo.png")
        print("icon_path", icon_path)
        self.setWindowIcon(QIcon(icon_path))
        # self.setFixedWidth(301)
        # self.setFixedHeight(471)
        self.initUI()
        self.toolbox = QToolBox()
        layout = self.ui.module_settings_layout
        layout.addWidget(self.toolbox)

        self.update_modules()

    def initUI(self):
        loader = QUiLoader()
        UI_VERSION = "05"
        UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interface", "ui", f"WD_Rig_Builder_{UI_VERSION}.ui")
        print(f"UI file path: {UI_FILE}")  # Debug: Print the UI file path
        if not os.path.exists(UI_FILE):
            cmds.error(f"ERROR: UI file does not exist: {UI_FILE}")

        file = QFile(UI_FILE)
        if not file.open(QFile.ReadOnly):
            cmds.error(f"ERROR: Unable to open UI file: {UI_FILE}")

        self.ui = loader.load(file, parentWidget=self)
        file.close()

        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"interface","style","style.css")
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.ui.setStyleSheet(stylesheet)

    def update_modules(self):
        files = [".".join(f.split(".")[:-1]) for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))]
        try: files.remove("")
        except ValueError: pass
        files = [f for f in files if f not in ["__init__", "hand"]]

        layout = self.ui.module_layout

        for module in files:
            button = QPushButton(module)
            button.setObjectName(f"button_{module}")
            layout.addWidget(button)

            QObject.connect(button, SIGNAL("clicked()"), lambda m=module: self.button_clicked(m))

    def button_clicked(self, module):
        print(f'Button clicked: {module}')
        page = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"This is {module}"))
        page.setLayout(layout)
        self.toolbox.addItem(page, module)


def main():
    ui = QtSampler()
    ui.show()
    return ui
