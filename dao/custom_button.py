import sys

from PyQt5.QtCore import pyqtSignal

from ui import Ui_label_img

sys.path.append("..")

from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton


class CustomButton(QPushButton):
    def __init__(self, tag: QLabel, url):
        super().__init__()
        self.url = url
        self.label = tag
        self.setMaximumSize(20, 20)
        self.setStyleSheet("border: 1px solid white;border-radius: 3px;")
        self.signal_send_url = pyqtSignal(str)

    def enterEvent(self, event) -> None:
        self.label.show()

    def leaveEvent(self, event) -> None:
        self.label.hide()

    def mousePressEvent(self, event) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.label.hide()
            self.label_widget = Ui_label_img.Ui_MainWindow(self.url)
            self.label_widget.show()
