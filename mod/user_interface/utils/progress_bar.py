import os
from maya import OpenMayaUI as omui
import maya.cmds as cmds

from mod.user_interface.utils import qtpyside
PySide, wrapInstance = qtpyside.get_version()

from PySide.QtCore import Qt, QTimer, QElapsedTimer
from PySide.QtWidgets import (
        QWidget,
        QProgressBar,
        QVBoxLayout,
        QLabel
        )

class ProgressBar(QWidget):
    def __init__(self, range=None, parent_widget=None):
        super().__init__(parent_widget)
        self.delete_old_ui()

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Progress")
        self.setObjectName("mod_progress")
        self.setAutoFillBackground(True)
        self.range = range*10

        self.init_ui()
        self.position_ui(parent_widget)

    def init_ui(self): 
        self.layout = QVBoxLayout(self)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.range)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        self.label = QLabel()
        self.layout.addWidget(self.label)
        self.elapsed_timer = QElapsedTimer()

        self.setLayout(self.layout)
        self.timer = QTimer(self)

        self.update()

    def position_ui(self, parent_widget):
        pos = parent_widget.pos()
        x = pos.x() + 200
        y = pos.y() + 350
        self.move(x, y)

    def delete_old_ui(self):
        if cmds.window("mod_progress", exists=True):
            cmds.deleteUI("mod_progress", window=True)
    
    def showEvent(self, event):
        super().showEvent(event)
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","style","style.css")
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)


    def start_progress(self):
        self.progress_bar.setValue(0)
        self.label.setText("Launching Processes...")
        self.show()
        self.elapsed_timer.start()
        self.timer.start(100)
        
    def update_progress(self):
        current_value = self.progress_bar.value()
        if current_value < self.range:
            self.progress_bar.setValue(current_value + 10)
            self.update()
    
    def stop_progress(self):
        self.timer.stop()
        elapsed_time_ms = self.elapsed_timer.elapsed()
        elapsed_time_sec = elapsed_time_ms / 1000.0
        print(f"Task completed in {elapsed_time_sec:.2f} seconds")

        self.hide()
        self.close()
        self.deleteLater()

    def update_label(self, text=None):
        self.label.setText(text)
