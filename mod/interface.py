import maya.cmds as cmds
from maya import OpenMayaUI as omui
import importlib
import os.path

from mod.user_interface.utils import qtpyside
PySide, wrapInstance = qtpyside.get_version()

from PySide.QtCore import Qt
from PySide.QtGui import QIcon
from PySide.QtWidgets import (QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QScrollArea,
                               QLabel,
                               QSizePolicy,
                               QLineEdit)

from mod.user_interface.pages import module_settings, sidebar, page_utils
from mod.systems import hands, joints, twist_joints, ik, fk, ribbon, squash_and_stretch
from mod.systems.utils import connect_modules, system_group, ikfk_switch, utils, reverse_foot, space_swap, reverse_foot_tmp
from mod.guides import create_guides, guide_data, mirror_rig

ui_pages = [module_settings, sidebar, page_utils]
systems = [create_guides, hands, joints, twist_joints, ik, fk, ribbon, squash_and_stretch]
system_util = [guide_data, mirror_rig, connect_modules, system_group, ikfk_switch, utils, reverse_foot, space_swap, reverse_foot_tmp]
for module_list in [ui_pages, systems, system_util]:
    for module in module_list:    
        importlib.reload(module)
        #print(f"DEBUG: reloaded {module}")

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)


class Interface(QWidget):
    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)
        UI_NAME = "MOD"
        self.systems_to_be_made = {}
        self.created_guides = []
        self.systems_to_be_deleted_polished = []
        
        self.check_existing_uis(UI_NAME)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.initUI()
        self.setFixedWidth(600)
        self.setFixedHeight(700)
        self.setWindowTitle(UI_NAME)
        self.setObjectName(UI_NAME)

    def initUI(self):
        if cmds.objExists("ui_data"):
            self.last_selected_button = cmds.getAttr("ui_data.ui_status", asString=True)
            self.rig_name_str = cmds.getAttr("ui_data.rig_name", asString=True)
        else:
            cmds.spaceLocator(n="ui_data")
            cmds.addAttr("ui_data", ln="ui_status", at="enum", enumName="guides:skeleton:rig:polish", k=True)
            cmds.addAttr("ui_data", ln="rig_name", dt="string", k=True)
            cmds.setAttr("ui_data.rig_name", "MMR_Rig", type="string")
            cmds.select(clear=True)
            self.last_selected_button = "guides"
            self.rig_name_str = "MMR_Rig"

        # layout
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Main layout
        self.main_layout_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_layout_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setStretch(1,100)
        self.vertical_layout.addWidget(self.main_layout_widget)

        # Rig Progress
        rig_progress_instance = page_utils.RigProgression(self, self.vertical_layout)

        # sidebar for modules
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMaximumWidth(100)
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.sidebar_layout.setSpacing(2)
        add_available_modules_instance = sidebar.AddAvailableModules(self, self.sidebar_layout)
        rig_name_instance = sidebar.RigNameWidget(self.sidebar_layout, self.rig_name_str)
        colour_widget_instance = sidebar.RigColourWidget(self.sidebar_layout)
        self.main_layout.addWidget(self.sidebar_widget)

        # main settings area
        self.module_widget = QWidget()
        self.module_widget.setMaximumWidth(500)
        self.module_layout = QVBoxLayout(self.module_widget)
        self.module_layout.setSizeConstraint(QVBoxLayout.SetMaximumSize)
        self.init_mainsettings()
        self.main_layout.addWidget(self.module_widget)

        # set stylesheet
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"user_interface","style","style.css")
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        # set ui icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"interface","images","UI_Logo.png")
        self.setWindowIcon(QIcon(icon_path))

    def check_existing_uis(self, UI_NAME):
        if cmds.window(UI_NAME, exists=True):
            cmds.deleteUI(UI_NAME, window=True)

    def init_mainsettings(self):
        settings_label = QLabel("SETTINGS:")
        settings_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settings_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 20px;
            }
        """)
        self.module_layout.addWidget(settings_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        container_widget = QWidget()

        # Ensure the container widget expands horizontally
        container_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.scroll_area_layout = QVBoxLayout(container_widget)
        self.scroll_area_layout.setSpacing(5)

        # Remove margins and align to top left
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll_area.setWidget(container_widget)
        self.scroll_area.setWidgetResizable(True)
        self.module_layout.addWidget(self.scroll_area)

        self.init_existingguides()

    def init_existingguides(self):
        guide_data_dict = guide_data.init_data()
        for key in guide_data_dict.values():
            print(key)
            try: print(key['hidden_obj'])
            except KeyError: print(f"hidden_obj dont exist on {key['master_guide']}")

        for data_guide in guide_data_dict.values():
            self.created_guides.append(data_guide["master_guide"])
            page = QWidget()
            page.setObjectName(f"parentWidget_{data_guide['master_guide']}")
            page.setStyleSheet(f"QWidget#parentWidget_{data_guide['master_guide']} {{ background-color: #25292c; }}")

            if "master" in data_guide["master_guide"]:
                module_name = data_guide["master_guide"].replace("master_","")
            else: module_name = data_guide["master_guide"]
            layout = QVBoxLayout(page)
            button = QPushButton(module_name)
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(button)

            settings_page_instance = module_settings.CreateModuleTab(self, module_name, button, page, self.scroll_area_layout, layout, data_guide)

            self.scroll_area_layout.insertWidget(0,page)

            self.systems_to_be_made[data_guide["master_guide"]] = data_guide

    def add_module(self, module):
        module_path = importlib.import_module(f"mod.modules.{module}")
        importlib.reload(module_path)
        if module_path.is_preset is True:
            for module in module_path.module_to_be_made.keys():
                self.add_module_instance(module, preset=module_path)
        else:
            self.add_module_instance(module, preset=None)

    def add_module_instance(self, module, preset):
        createdmodule_instance = module_settings.AddModule(module, preset)
        module_dict = createdmodule_instance.return_data()
        count_nested_dicts = sum(1 for value in module_dict.values() if isinstance(value, dict))
        self.created_guides.append(module_dict["master_guide"])
        if "hand" in module_dict["module"]:
            module_name = module_dict["name"]
        elif "master" in module_dict["master_guide"]:
            module_name = module_dict["master_guide"].replace("master_","")
        else: module_name = module_dict["master_guide"]

        page = QWidget()
        page.setObjectName(f"parentWidget_{module_dict['master_guide']}")
        page.setStyleSheet(f"QWidget#parentWidget_{module_dict['master_guide']} {{ background-color: #25292c; }}")

        layout = QVBoxLayout(page)
        button = QPushButton(module_name)
        button.setCheckable(True)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(button)

        settings_page_instance = module_settings.CreateModuleTab(self, module_name, button, page, self.scroll_area_layout, layout, module_dict)

        self.scroll_area_layout.insertWidget(0,page)
        
        if count_nested_dicts > 1:
            for sub_dict in module_dict.values():
                if isinstance(sub_dict, dict):
                    self.systems_to_be_made[sub_dict["master_guide"]] = sub_dict
        else:
            self.systems_to_be_made[module_dict["master_guide"]] = module_dict

    def create_joints(self):
        orientation = "xyz"

        mirror_module = mirror_rig.mirror_data(self.systems_to_be_made, orientation)
        self.systems_to_be_made = mirror_module.get_mirror_data()
        created_guides = [key["master_guide"] for key in self.systems_to_be_made.values()]

        rig_jnt_list = joints.get_joint_list(orientation,created_guides, system="rig")
        num = 0
        for dict in self.systems_to_be_made.values():
            if not dict["joints"]:
                dict["joints"] = rig_jnt_list[num]
            num = num+1

        self.skn_jnt_list = joints.get_joint_list(orientation,created_guides, system="skn")

        for key in self.systems_to_be_made.values():
            twist_joint = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_twist_jnts", asString=1)
            if twist_joint == "Yes":
                twist_amount = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_twist_amount")
                if twist_amount > 0:
                    rig_twist_instance = twist_joints.PrepSkeleton(orientation,key,system="rig")
                    rig_twist_data = rig_twist_instance.return_data()
                    rig_twist_list = rig_twist_data["return_data_list"]
                    tweak_joint_dict = rig_twist_data["tweak_joint_dict"]
                    twist_joints.PrepSkeleton(orientation,key,system="skn")
                    twist_joints.rig_to_skn(rig_twist_list)
                    key.update({"twist_dict": rig_twist_list})
                    key.update({"tweak_dict": tweak_joint_dict})

        connect_modules.attach_joints(self.systems_to_be_made,system="rig")
        connect_modules.attach_joints(self.systems_to_be_made,system="skn")

        self.skn_jnt_list = [item for sublist in self.skn_jnt_list for item in sublist]
        for joint in self.skn_jnt_list: cmds.parentConstraint(f"jnt_rig{joint[7:]}",joint,mo=1,n=f"pConst_jnt_rig{joint[7:]}")

        for module in self.created_guides:
            pushButton = self.module_widget.findChild(QPushButton, f"button_remove_{module}")
            pushButton.setEnabled(False)

        cmds.select(cl=1)

    def create_rig(self):
        for key in self.systems_to_be_made.values():
            master_guide = key['master_guide']
            rig_type = cmds.getAttr(f"{master_guide}.{master_guide}_rig_type", asString=1)
            orientation = "xyz"

            # sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"systems","modules"))
            module = importlib.import_module(f"mod.modules.{key['module']}")
            importlib.reload(module)
            try: delete_end = module.delete_end
            except AttributeError: delete_end = False
            if "root" in key["module"]: pass
            else:
                if rig_type == "FK":
                    fk_joint_list = joints.joint(orientation, master_guide, system="fk", )
                    fk_module = fk.create_fk(fk_joint_list,master_guide,key["guide_scale"],delete_end=delete_end)
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
                    fk_module = fk.create_fk(fk_joint_list,master_guide,key["guide_scale"],delete_end=delete_end)
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
                            if module.ik_joints["ik_type"] == "quadruped":
                                reverse_foot_instance = reverse_foot_tmp.CreateReverseFootQuadruped(key["module"],key)
                            if module.ik_joints["ik_type"] == "biped":
                                reverse_foot_instance = reverse_foot_tmp.CreateReverseFootBiped(key["module"],key)
                    except KeyError:
                        print(f"Didnt find rev_locators in key not making reverse foot for: {key}")
                    squash_stretch_attr = cmds.getAttr(f"{master_guide}.{master_guide}_squash_stretch", asString=True)
                    if squash_stretch_attr == "Yes":
                        squash_and_stretch_instance = squash_and_stretch.CreateSquashAndStretch(key, module.ik_joints)

                if cmds.getAttr(f"{master_guide}.{master_guide}_twist_jnts", asString=True) == "Yes":
                    twist_joints.CreateTweaks(tweak_joint_dict=key["tweak_dict"])

        rig_name = self.sidebar_widget.findChild(QLineEdit, "rig_name")
        system_group.grpSetup(rig_name.text())
        cmds.setAttr("ui_data.rig_name", str(rig_name.text()), type="string")

        for key in self.systems_to_be_made.values():  # seperate loop to be sure systems are made before connecting
            rig_type = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_rig_type", asString=1)
            twist_joint = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_twist_jnts", asString=1)
            if key['system_to_connect']:
                systems_to_connect = key['system_to_connect']
                connect_modules.connect_polished(systems_to_connect)
            if rig_type == "FKIK":
                space_swap_module = space_swap.SpaceSwapping(key)

        button_names = ["L_colour","C_colour","R_colour"]
        button_colour_dict = {"L_colour":[],"C_colour":[],"R_colour":[]}
        for x in button_names:
            button_name = self.sidebar_widget.findChild(QPushButton, x)
            palette = button_name.palette()
            button_colour = palette.color(button_name.backgroundRole())
            button_rgb = button_colour.getRgb()
            button_colour_dict[x] = list(button_rgb)
        button_colour_dict.update({"root": [0,255,0]})

        ctrl_list = cmds.ls("ctrl_*",type="transform")
        utils.colour_controls(ctrl_list,button_colour_dict)

        system_group.heirachy_parenting(self.systems_to_be_made)

        cmds.select(cl=1)

    def remove_module(self, master_guide, settings_page):
        for key in list(self.systems_to_be_made.values()):
            if master_guide in key['master_guide']:
                if self.systems_to_be_made[master_guide]["rev_locators"]:
                    cmds.delete(self.systems_to_be_made[master_guide]["rev_locators"])
                if cmds.ls(master_guide):
                    cmds.delete(master_guide, key['connectors'])
                else:
                    cmds.warning(f"{master_guide} not found proceeding to remove module.")
                    cmds.delete(key['connectors'])

                self.systems_to_be_made.pop(master_guide)
                self.created_guides.remove(master_guide)

        self.settings_page_widget = self.findChild(QWidget, settings_page)
        self.settings_page_widget.deleteLater()

    def update_rig(self, button):
        rig_name = self.sidebar_widget.findChild(QLineEdit, "rig_name")
        if button == "guides":
            if self.last_selected_button == "skeleton":
                utils.hide_guides(self.systems_to_be_made, self.created_guides, module_widget=self.module_widget, hidden=False)
                utils.delete_joints(self.systems_to_be_made, self.skn_jnt_list)
            elif self.last_selected_button == "rig":
                utils.hide_guides(self.systems_to_be_made, self.created_guides, module_widget=self.module_widget, hidden=False)
                cmds.delete(rig_name.text())
            elif self.last_selected_button == "polish":
                cmds.warning("Rig has been polished past data has been deleted")

        elif button == "skeleton":
            if self.last_selected_button == "guides":
                self.create_joints()
                utils.hide_guides(self.systems_to_be_made, self.created_guides, module_widget=self.module_widget, hidden=True)
            elif self.last_selected_button == "rig" or self.last_selected_button == "polish":
                cmds.delete(rig_name.text())
                self.create_joints()

        elif button == "rig":
            if self.last_selected_button == "guides":
                self.create_joints()
                utils.hide_guides(self.systems_to_be_made, self.created_guides, module_widget=self.module_widget, hidden=True)
                self.create_rig()
            elif self.last_selected_button == "skeleton":
                self.create_rig()
            elif self.last_selected_button == "polish":
                cmds.warning("Rig has been polished past data has been deleted")

        self.last_selected_button = button
        enum_options = cmds.attributeQuery("ui_status", node="ui_data", listEnum=True)
        enum_list = enum_options[0].split(":")
        if button in enum_list:
            index = enum_list.index(button)
            cmds.setAttr("ui_data.ui_status", index)


def main():
    ui = Interface()
    ui.show()
    return ui
