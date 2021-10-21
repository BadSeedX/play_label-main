
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
import cv2
import numpy as np


class CustomProTagLabel(QLabel):
    def __init__(self, url):
        super(CustomProTagLabel, self).__init__()
        self.setFixedSize(200,100)

        pic = cv2.imdecode(np.fromfile(url,dtype=np.uint8),-1)
        pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
        x = pic.shape[1]
        y = pic.shape[0]
        self.zoom_scale = 1
        frame = QImage(pic, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.setPixmap(pix)
        self.setScaledContents(True)