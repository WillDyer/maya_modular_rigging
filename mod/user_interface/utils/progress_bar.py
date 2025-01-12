import os
from maya import OpenMayaUI as omui

from mod.user_interface.utils import qtpyside
PySide, wrapInstance = qtpyside.get_version()

from PySide.QtCore import Qt, QTimer
from PySide.QtWidgets import (
        QWidget,
        QProgressBar,
        QVBoxLayout,
        QLabel
        )

class ProgressBar(QWidget):
    def __init__(self, range=None):
        super().__init__()
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Progress")
        self.setObjectName("mod_progress")
        self.setAutoFillBackground(True)
        self.range = range*10
        
        self.layout = QVBoxLayout(self)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.range)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        
        self.label = QLabel()
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)
        self.timer = QTimer(self)
    
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
        self.timer.start(100)
        
    def update_progress(self):
        current_value = self.progress_bar.value()
        if current_value < self.range:
            self.progress_bar.setValue(current_value + 10)
    
    def stop_progress(self):
        self.timer.stop()
        self.setParent(None)
        self.close()
        self.deleteLater()

    def update_label(self, text=None):
        self.label.setText(text)
