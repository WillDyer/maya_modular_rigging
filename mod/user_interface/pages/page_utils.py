from mod.user_interface.utils import qtpyside
PySide, wrapInstance = qtpyside.get_version()

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWidgets import QWidget
from PySide.QtWidgets import *
from PySide.QtUiTools import *

import maya.cmds as cmds


class RigProgression(QWidget):
    def __init__(self, interface_class, vertical_layout):
        super().__init__()
        self.vertical_layout = vertical_layout
        self.interface_class = interface_class
        self.init_ui()

    def init_ui(self):
        self.rig_layout_widget = QWidget()
        self.rig_layout = QHBoxLayout(self.rig_layout_widget)
        self.rig_layout.setContentsMargins(5, 5, 5, 5)
        self.rig_layout.setSpacing(0)
        self.rig_layout_widget.setStyleSheet(""" QPushButton { border-radius: 0px; font-weight: bold; } """)

        self.button_group = QButtonGroup(self.rig_layout_widget)
        self.button_group.setExclusive(True)

        self.rig_progression_buttons()
        self.vertical_layout.addWidget(self.rig_layout_widget)

    def rig_progression_buttons(self):
        self.guides_button = QPushButton("Guides")
        self.guides_button.setObjectName("button_guides")
        self.guides_button.setCheckable(True)
        # self.guides_button.setChecked(True)
        self.button_group.addButton(self.guides_button)

        self.skeleton_button = QPushButton("Skeleton")
        self.skeleton_button.setObjectName("button_skeleton")
        self.skeleton_button.setCheckable(True)
        self.button_group.addButton(self.skeleton_button)

        self.rig_button = QPushButton("Rig")
        self.rig_button.setObjectName("button_rig")
        self.rig_button.setCheckable(True)
        self.button_group.addButton(self.rig_button)

        self.polish_button = QPushButton("Polish")
        self.polish_button.setObjectName("button_polish")
        self.polish_button.setCheckable(True)
        self.button_group.addButton(self.polish_button)

        self.rig_layout.addWidget(self.guides_button)
        self.rig_layout.addWidget(self.skeleton_button)
        self.rig_layout.addWidget(self.rig_button)
        self.rig_layout.addWidget(self.polish_button)

        if cmds.objExists("ui_data"):
            active_button = cmds.getAttr("ui_data.ui_status", asString=True)
            button = getattr(self, f"{active_button}_button", None)
            button.setChecked(True)

        QObject.connect(self.guides_button, SIGNAL("clicked()"), lambda: self.interface_class.update_rig(button="guides"))
        QObject.connect(self.skeleton_button, SIGNAL("clicked()"), lambda: self.interface_class.update_rig(button="skeleton"))
        QObject.connect(self.rig_button, SIGNAL("clicked()"), lambda: self.interface_class.update_rig(button="rig"))
        QObject.connect(self.polish_button, SIGNAL("clicked()"), lambda: self.interface_class.update_rig(button="polish"))
