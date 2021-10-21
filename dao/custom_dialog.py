import os
import sys

from PyQt5.QtWidgets import QDialog
sys.path.append("..")

from ui.Ui_info import Ui_Dialog

class CustomDialog(Ui_Dialog, QDialog):
    message = {
        0 : "您已标注为无异常",
        1 : "您已标注为鸟类",
        2 : "您已标注为轻飘物（塑料袋、包装等）",
        3 : "您已标注为树枝",
        4 : "您已保存标注图像至路径 ： "
    }


    def __init__(self, message_num, url = ""):
        super(Ui_Dialog, self).__init__()
        self.setupUi(self)
        self.label_msg.setText(self.message[message_num] + url)
        self.label_msg.setWordWrap(True)
        
        