from PyQt5 import QtCore
from PyQt5.QtCore import QRect, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QLabel, QWidget, QMessageBox, QScrollArea
from qtpy import QtGui

from ui import Ui_select_class


class MyLabel(QLabel):  # 自定义标签控件
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0

    drawing_rec = False  # 绘制中目标检测框
    drawn_rec = False  # 已绘制但未确认目标检测框
    rect = QRect(0, 0, 0, 0)
    rects = []  # 检测框列表
    labels = []  # 检测框对应的类别列表
    img_path = ""
    scale = 1.
    w, h = 960, 540

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and not self.drawing_rec:
            self.setMouseTracking(True)

            self.drawing_rec = True
            self.drawn_rec = False

            self.x0, self.y0 = event.x(), event.y()
        elif event.buttons() == QtCore.Qt.LeftButton and self.drawing_rec:
            self.drawing_rec = False
            self.drawn_rec = True

            self.x1, self.y1 = event.x(), event.y()
            x_min = min(self.x0, self.x1)
            y_min = min(self.y0, self.y1)
            self.rect = QRect(x_min, y_min, abs(self.x1 - self.x0), abs(self.y1 - self.y0))

            # 跳出人工标注界面
            self.label_window = Ui_select_class.Ui_MainWindow()
            self.label_window.signal_confirm.connect(self.confirm_emit_slot)
            self.label_window.show()
        elif event.buttons() == QtCore.Qt.RightButton:
            # 跳出撤销对话框
            if self.drawn_rec | self.drawing_rec:
                undo_message = QMessageBox.information(self, "提示信息", "撤销目标框", QMessageBox.Yes | QMessageBox.Cancel)
                if undo_message == QMessageBox.Yes:
                    self.drawn_rec = False                      # undo操作
                    self.drawing_rec = False
                    self.update()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:                          # 图片放大
            self.scale += 0.1
            jpg = QtGui.QPixmap(self.img_path).scaled(self.w * self.scale, self.h * self.scale)
            self.setPixmap(jpg)
            self.adjustSize()
            self.update()
        else:                                                   # 图片缩小
            if self.scale >= 1.1:
                self.scale -= 0.1
                jpg = QtGui.QPixmap(self.img_path).scaled(self.w * self.scale, self.h * self.scale)
                self.setPixmap(jpg)
                self.adjustSize()
                self.update()


    def mouseMoveEvent(self, event):
        if self.drawing_rec:
            self.x1, self.y1 = event.x(), event.y()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)  # 定义画笔
        if self.drawing_rec | self.drawn_rec:  # 正在绘制矩形框或已经绘制矩形框但未确认
            x_min, y_min = min(self.x0, self.x1), min(self.y0, self.y1)  # 确定上坐标
            rect = QRect(x_min, y_min, abs(self.x1 - self.x0), abs(self.y1 - self.y0))

            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))  # 设置画笔为绿色
            painter.drawRect(rect)

        if self.rects:  # 已确认矩形框列表，画笔设置为红色
            for rect in self.rects:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(rect)

    def confirm_emit_slot(self, add_rects, cls):  # 槽函数
        if add_rects:
            self.rects.append(self.rect)  # 加入列表
            self.labels.append(cls)
            self.update()  # 更新

        else:
            self.drawn_rec = False  # 取消未确认的矩形框
            self.update()


