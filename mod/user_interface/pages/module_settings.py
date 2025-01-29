from mod.user_interface.utils import qtpyside
PySide, wrapInstance = qtpyside.get_version()

from PySide.QtCore import Qt, QObject, SIGNAL
from PySide.QtWidgets import (QWidget,
                               QHBoxLayout,
                               QPushButton,
                               QLabel,
                               QSizePolicy,
                               QFormLayout,
                               QComboBox,
                               QSpinBox,
                               QCheckBox)
import maya.cmds as cmds
import importlib

from mod.rig.utils import hands
from mod.guides import create_guides, guide_data

importlib.reload(create_guides)
importlib.reload(hands)
importlib.reload(guide_data)


class CreateModuleTab(QWidget):
    def __init__(self, interface_class, module, button, page, scroll_area_layout, layout, module_dict):
        super().__init__()
        self.module_path = importlib.import_module(f"mod.modules.{module_dict['module']}")
        importlib.reload(self.module_path)

        self.module = module
        self.button = button
        self.page = page
        self.scroll_area_layout = scroll_area_layout
        self.module_layout = layout
        self.module_dict = module_dict
        self.master_guide = self.module_dict["master_guide"]
        self.interface_class = interface_class

        self.settings_page = QWidget()
        self.settings_page.setObjectName("settings_page")
        self.settings_page.setStyleSheet(""" QWidget#settings_page { background-color: #25292c;} """)
        self.settings_layout = QFormLayout(self.settings_page)
        self.settings_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.parent_joint_widget()
        self.ikfk_widget()
        self.orientation_widget()
        self.offset_widget()
        self.remove_module()

        checkbox = self.move_widget_dropdown()
        self.move_widget(checkbox)

        self.settings_page.hide()

    def parent_joint_widget(self):
        # parent joint
        parent_label = QLabel("Parent:")
        parent_combobox = QComboBox()
        parent_combobox.setObjectName(f"combobox_parent_{self.module}")
        parent_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if self.module_dict["system_to_connect"]: parent_combobox.addItem(self.module_dict["system_to_connect"][1])
        else: parent_combobox.addItem("World")

        self.settings_layout.addRow(parent_label, parent_combobox)

    def ikfk_widget(self):
        def set_ikfk_attr(ikfk_combobox):
            value = ikfk_combobox.currentText()
            value = self.module_path.available_rig_types.index(value)
            # cmds.setAttr(f"{self.master_guide}.{self.master_guide}_rig_type", value)

        # IKFK Default
        ikfk_label = QLabel("IKFK Default:")
        ikfk_combobox = QComboBox()
        ikfk_combobox.setObjectName(f"combobox_ikfk_{self.module}")
        ikfk_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        ikfk_combobox.addItems(self.module_path.available_rig_types)
        ikfk_combobox.currentIndexChanged.connect(set_ikfk_attr(ikfk_combobox))
        QObject.connect(ikfk_combobox, SIGNAL("currentIndexChanged(int)"), lambda: set_ikfk_attr(ikfk_combobox))

        self.settings_layout.addRow(ikfk_label, ikfk_combobox)

    def orientation_widget(self):
        # Orientation
        orientation_label = QLabel("Orientation:")
        orientation_combobox = QComboBox()
        orientation_combobox.setObjectName(f"combobox_orientation_{self.module}")
        orientation_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        available_orientations = ["xyz","yzx","zxy"]
        orientation_combobox.addItems(available_orientations)
        index = available_orientations.index("xyz")
        orientation_combobox.setCurrentIndex(index)

        self.settings_layout.addRow(orientation_label, orientation_combobox)

    def offset_widget(self):
        def offset_guide(offset_widget):
            XButton = offset_widget.findChild(QSpinBox, f"spinbox_offsetX_{self.module}")
            YButton = offset_widget.findChild(QSpinBox, f"spinbox_offsetY_{self.module}")
            ZButton = offset_widget.findChild(QSpinBox, f"spinbox_offsetZ_{self.module}")
            cmds.xform(self.module_dict["master_guide"], r=True, translation=[XButton.value(), YButton.value(), ZButton.value()])
            for xyz in [XButton, YButton, ZButton]:
                xyz.setValue(0)

        # offset
        offset_label = QLabel("Offset:")
        offset_widget = QWidget()
        offset_widget.setObjectName("offsetWidget")
        offset_widget.setContentsMargins(0, 0, 0, 0)
        offset_widget.setStyleSheet(""" QWidget#offsetWidget { background-color: #25292c; } """)
        offset_horizontal_layout = QHBoxLayout(offset_widget)
        offset_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        for xyz in ["X","Y","Z"]:
            spin_box = QSpinBox()
            spin_box.setObjectName(f"spinbox_offset{xyz}_{self.module}")
            spin_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            spin_box.setMinimum(-2**31)
            spin_box.setMaximum(2**31 - 1)
            spin_box.setFixedWidth(55)
            offset_horizontal_layout.addWidget(spin_box)
        offset_move_button = QPushButton("Move")
        offset_horizontal_layout.addWidget(offset_move_button)
        QObject.connect(offset_move_button, SIGNAL("clicked()"), lambda: offset_guide(offset_widget))

        self.settings_layout.addRow(offset_label, offset_widget)

    def remove_module(self):
        # remove module
        remove_module = QPushButton("Remove Module")
        remove_module.setObjectName(f"button_remove_{self.master_guide}")

        self.settings_layout.addRow(remove_module)
        QObject.connect(remove_module, SIGNAL("clicked()"), lambda: self.interface_class.remove_module(self.master_guide, settings_page=f"parentWidget_{self.master_guide}"))

    def move_widget_dropdown(self):
        # move widget settings
        checkbox = QCheckBox('Expand/Collapse')
        checkbox.setObjectName("checkbox")
        checkbox.setStyleSheet(""" QWidget#checkbox { background-color: #25292c;} """)

        self.settings_layout.addRow(checkbox)
        return checkbox

    def move_widget(self, checkbox):
        def move_widgets(page, button):
            page = page
            button = button

            def move_widget(updown):
                index = self.scroll_area_layout.indexOf(page)
                new_index = index + updown
                if new_index < 0 or new_index >= self.scroll_area_layout.count():
                    return
                self.scroll_area_layout.insertWidget(new_index, page)

            if "top" in button:
                self.scroll_area_layout.insertWidget(0,page)
            elif "up" in button:
                move_widget(-1)
            elif "down" in button:
                move_widget(1)

        def widget_settings(button, collapse_button, move_widget):
            if button.isChecked() and collapse_button.isChecked():
                move_widget.show()
            else:
                move_widget.hide()

        # move widget
        move_widget = QWidget()
        move_widget.setObjectName("move_widget")
        move_widget.setStyleSheet(""" QWidget#move_widget { background-color: #25292c;} """)
        move_widget_layout = QHBoxLayout(move_widget)
        move_list = []
        # for move in ["Move Up","Move Down","To Top"]:
        moveup_button = QPushButton("move_up")
        move_widget_layout.addWidget(moveup_button)
        movedown_button = QPushButton("move_down")
        move_widget_layout.addWidget(movedown_button)
        movetop_button = QPushButton("to_top")
        move_widget_layout.addWidget(movetop_button)

        QObject.connect(moveup_button, SIGNAL("clicked()"), lambda: move_widgets(self.page, button="up"))
        QObject.connect(movedown_button, SIGNAL("clicked()"), lambda: move_widgets(self.page, button="down"))
        QObject.connect(movetop_button, SIGNAL("clicked()"), lambda: move_widgets(self.page, button="top"))

        move_widget.hide()
        QObject.connect(checkbox, SIGNAL("clicked()"), lambda: widget_settings(self.button, checkbox, move_widget))

        # add to the settings_layout
        self.settings_layout.addRow(move_widget)

        self.module_layout.addWidget(self.settings_page)
        QObject.connect(self.button, SIGNAL("clicked()"), lambda: self.drop_downs(self.settings_page))

    def drop_downs(self, settings_page):
        width = self.page.size().width()

        if self.button.isChecked():
            settings_page.show()
        else:
            settings_page.hide()


class AddModule():
    def __init__(self, module, preset):
        self.created_guides = []
        self.systems_to_be_made = {}
        self.add_module(module, preset)

    def add_module(self, module, preset):
        module_path = importlib.import_module(f"mod.modules.{module}")
        importlib.reload(module_path)
        offset = [
            0,0,0
        ]

        attach_to = []
        if preset:
            if preset.module_to_be_made[module] == "world": pass
            else:
                attach_to = [cmds.ls(f"*{preset.module_to_be_made[module]}", type="transform")[0]]
        
        if module == "hand":
            selection = cmds.ls(sl=1)[0]
            self.guides = hands.create_hands(selection, self.systems_to_be_made, self.created_guides, 5)
            self.temp_dict = self.guides.get_dict()
        else:
            self.guides = create_guides.Guides(module,offset,module_path.side,to_connect_to=attach_to,use_existing_attr=[])
            self.add_module_properties(module_path, module)

    def add_module_properties(self, module_path, module):
        guide = self.guides.collect_guides()
        if guide:
            master_guide = guide["master_guide"]
            guide_connector_list = guide["connector_list"]
            system_to_connect = guide["system_to_connect"]
            guide_list = guide["ui_guide_list"]
            data_guide = guide["data_guide"]
            guide_number = guide["guide_number"]
            if "rev_locators" in guide: rev_locators = guide["rev_locators"]
            else: rev_locators = []
            self.created_guides.append(master_guide)
            # self.ui.skeleton_box.setEnabled(True)

            print(f"Module: {module}")
            print(f"Master Guide: {master_guide}")
            print(f"Created Guides: {self.created_guides}")

            self.temp_dict = {
                "module": module,
                "master_guide": master_guide,
                "guide_list": guide_list,
                "guide_scale": module_path.guide_scale,
                "joints": [],
                "side": module_path.side,
                "connectors": guide_connector_list,
                "system_to_connect": system_to_connect,
                "space_swap": module_path.space_swapping,
                "ik_ctrl_list": [],
                "fk_ctrl_list": [],
                "ik_joint_list": [],
                "fk_joint_list": [],
                "rev_locators": rev_locators,
                "hidden_obj": master_guide,
                "guide_number": guide_number
            }
            # self.systems_to_be_made[master_guide] = temp_dict
            guide_data.setup(self.temp_dict, data_guide)

        cmds.select(clear=1)

    def return_data(self):
        return self.temp_dict
