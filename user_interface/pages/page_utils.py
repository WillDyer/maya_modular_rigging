from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *


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
        self.guides_button.setChecked(True)
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

        QObject.connect(self.guides_button, SIGNAL("clicked()"), lambda: self.interface_class.hide_guides(hidden=False))
        QObject.connect(self.guides_button, SIGNAL("clicked()"), lambda: self.interface_class.delete_joints())
        QObject.connect(self.skeleton_button, SIGNAL("clicked()"), lambda: self.interface_class.create_joints())
        QObject.connect(self.polish_button, SIGNAL("clicked()"), lambda: self.interface_class.polish_rig())
