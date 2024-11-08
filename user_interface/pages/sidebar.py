try:
    from PySide6.QtCore import QObject, SIGNAL
    from PySide6.QtGui import *
    from PySide6.QtWidgets import (QWidget,
                                   QSpacerItem,
                                   QLineEdit,
                                   QSizePolicy,
                                   QLabel,
                                   QPushButton,
                                   QHBoxLayout)
except ModuleNotFoundError:
    from PySide2.QtCore import QObject, SIGNAL
    from PySide2.QtGui import *
    from PySide2.QtWidgets import (QWidget,
                                   QSpacerItem,
                                   QLineEdit,
                                   QSizePolicy,
                                   QLabel,
                                   QPushButton,
                                   QHBoxLayout)

import importlib
import os.path
import string

from user_interface.pages import module_settings
importlib.reload(module_settings)


class AddAvailableModules(QWidget):
    def __init__(self, interface_class, sidebar_layout):
        super().__init__()
        self.interface_class = interface_class
        self.sidebar_layout = sidebar_layout
        self.update_modules()

    def update_modules(self):
        files = [".".join(f.split(".")[:-1]) for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'systems', 'modules'))]
        try: files.remove("")
        except ValueError: pass
        files = [f for f in files if f not in ["__init__", "hand"]]

        module_label = QLabel("MODULES:")
        module_label.setFixedSize(200,25)
        module_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 20px;
            }
        """)
        self.sidebar_layout.addWidget(module_label)

        for module in files:
            module_path = importlib.import_module(f"systems.modules.{module}")
            importlib.reload(module_path)
            if module_path.hide is False:
                button_name = module.replace("_", " ")
                button_name = string.capwords(button_name)
                # button_name = button_name.title()
                button = QPushButton(button_name)
                # button.setFixedSize(150,20)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                button.setObjectName(f"button_{module}")
                self.sidebar_layout.addWidget(button)

                QObject.connect(button, SIGNAL("clicked()"), lambda m=module: self.interface_class.add_module(m))

        spacer = QSpacerItem(20,40,QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sidebar_layout.addSpacerItem(spacer)


class RigColourWidget(QWidget):
    def __init__(self, sidebar_layout):
        super().__init__()
        self.sidebar_layout = sidebar_layout
        self.colour_settings()

    def colour_settings(self):
        colour_label = QLabel("RIG COLOURS:")
        colour_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 20px;
            }
        """)
        colour_widget = QWidget()
        horizontal_layout = QHBoxLayout(colour_widget)
        horizontal_layout.setContentsMargins(0, 5, 5, 0)
        L_button = QPushButton()
        L_button.setObjectName("L_colour")
        C_button = QPushButton()
        C_button.setObjectName("C_colour")
        R_button = QPushButton()
        R_button.setObjectName("R_colour")

        L_button.setStyleSheet("background-color: red;")
        C_button.setStyleSheet("background-color: yellow;")
        R_button.setStyleSheet("background-color: blue;")

        L_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        C_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        R_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        horizontal_layout.addWidget(L_button)
        horizontal_layout.addWidget(C_button)
        horizontal_layout.addWidget(R_button)

        self.sidebar_layout.addWidget(colour_label)
        self.sidebar_layout.addWidget(colour_widget)

        QObject.connect(L_button, SIGNAL("clicked()"), lambda: self.colour_button(L_button))
        QObject.connect(C_button, SIGNAL("clicked()"), lambda: self.colour_button(C_button))
        QObject.connect(R_button, SIGNAL("clicked()"), lambda: self.colour_button(R_button))

    def colour_button(self,button):
        colour = self.get_colour()
        if colour: button.setStyleSheet(f"background-color: rgb({colour['red']}, {colour['green']}, {colour['blue']});")

    def get_colour(self):
        colour = QColorDialog.getColor()
        if colour.isValid():
            red = colour.red()
            green = colour.green()
            blue = colour.blue()
            return {"red":red, "green":green, "blue":blue}
        else: return None


class RigNameWidget(QWidget):
    def __init__(self, sidebar_layout):
        super().__init__()
        self.sidebar_layout = sidebar_layout
        self.rig_name()

    def rig_name(self):
        rig_label = QLabel("RIG NAME:")
        rig_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 20px;
            }
        """)
        rig_widget = QLineEdit("WD_Rig_Master")
        rig_widget.setObjectName("rig_name")
        rig_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rig_widget.setContentsMargins(0, 5, 5, 0)

        self.sidebar_layout.addWidget(rig_label)
        self.sidebar_layout.addWidget(rig_widget)
