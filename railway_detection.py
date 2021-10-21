from dao.custom_label import CustomProTagLabel
from dao.custom_button import CustomButton
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui

from ui.railway_detection import Ui_MainWindow

from processor.img_processor import img_processor
from ui import Ui_label_img

import cv2
import time
import os
import sys

## 窗口类
class myMainWindow(Ui_MainWindow, QMainWindow):
    css = ""

    # 窗口初始化
    def __init__(self, worker_id=0):
        # 窗口初始化
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        # 槽函数
        self.btn_label_pic.clicked.connect(self.open_picture)
        self.btn_change_save_path.clicked.connect(self.change_save_path)
        self.btn_open_video.clicked.connect(self.openVideoFile)
        self.hslider_timeF.valueChanged.connect(self.valueChanged)

        # --------------------------------
        #   打开，关闭摄像头录制并保存视频
        # --------------------------------
        self.btn_open_camera.clicked.connect(self.openCamera)
        self.btn_close_camera.clicked.connect(self.closeCamera)

        #  初始化：获取id、是否打开文件、画笔
        self.worker_id = worker_id
        self.open_flag = False
        self.timeF = 25
        self.painter = QPainter(self)
        self.dir_path = None
        self.init_path = False
        self.i_processor = img_processor()
        self.bar_btn = []

    ## 打开摄像头
    def openCamera(self):
        try:
            self.video_stream = cv2.VideoCapture("http://admin:admin@10.2.63.76:8081/")
            # TODO 视频文件默认保存
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
            # 视频文件保存路径
            self.out = cv2.VideoWriter("output.avi", self.fourcc, 30.0, (640, 480))
            # frame_num = self.video_stream.get(7)
            self.probar_load.setMaximum(1000)
            # 打开视频后初始视频信息设置：打开文件、计数帧
            self.open_flag = True
            self.frame_index = 0
            self.saveVideo()
            """
            # 存储视频
            while (self.video_stream.isOpened()):
                ret, frame = self.video_stream.read()
                if ret == True:
                    self.out.write(frame)
                else:
                    break
            """

        except:
            print("open")

    ## 关闭摄像头
    def closeCamera(self):
        try:
            self.video_stream.release()
            self.out.release()
        except:
            print("close")

    ## 帧率变化函数
    def valueChanged(self):
        # 帧率设置，标签内容重置
        self.timeF = self.hslider_timeF.value()
        self.label_timeF.setText("处理帧率：" + str(self.timeF))

    ## 打开视频文件
    def openVideoFile(self):
        # 视频路径处理，去双斜杠\\
        self.url = QFileDialog.getOpenFileUrl()[0].url()[8:].replace('\\', '/')
        if self.url != "":
            # 获取视频信息
            self.get_video_info()
            # opencv读取视频
            self.video_stream = cv2.VideoCapture(self.url)
            frame_num = self.video_stream.get(7)
            self.probar_load.setMaximum(frame_num)
            # 打开视频后初始视频信息设置：打开文件、计数帧
            self.open_flag = True
            self.frame_index = 0

    ## 获取视频信息：视频名称，并写好异常图片保存路径：“./视频名称_result/”
    def get_video_info(self):
        info = self.url.split("/")[-1]
        self.video_name = info.split(".")[0]
        if self.dir_path == None:
            self.change_save_path()
            self.init_path = True
        self.video_error_path = self.dir_path + "/" + self.video_name + "_result/"

    ## 绘画事件
    def paintEvent(self, a0: QtGui.QPaintEvent):
        start_t = time.time()
        if self.open_flag:
            # 读帧
            ret, frame = self.video_stream.read()
            if ret == True:
                self.out.write(frame)
            self.frame_index = self.frame_index + 1

            if not frame is None:
                # 抽帧处理
                if self.frame_index % self.timeF == 0:
                    # 处理当前帧
                    self.frame = frame
                    self.i_processor.process(frame)
                    # 进度条前进
                    self.probar_load.setValue(self.frame_index)
                    # 异常则报错
                    if (self.i_processor.is_error):
                        self.alarm()
                    else:
                        self.normal()

                # 显示图片，画图
                frame = cv2.resize(frame, (891, 541), interpolation=cv2.INTER_AREA)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.Qframe = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3,
                                     QImage.Format_RGB888)
                self.label_in_img.setPixmap(QPixmap.fromImage(self.Qframe))

        end_t = time.time()
        duration = end_t - start_t
        # 控制播放/抽帧速度
        if (duration < 1 / self.timeF):
            time.sleep(1 / self.timeF - duration)

    # 预警
    def alarm(self):
        # 显示异常帧
        frame_showed = cv2.resize(self.frame, (631, 381), interpolation=cv2.INTER_AREA)
        frame_showed = cv2.cvtColor(frame_showed, cv2.COLOR_BGR2RGB)
        img_showed = QImage(frame_showed.data, frame_showed.shape[1], frame_showed.shape[0], frame_showed.shape[1] * 3,
                            QImage.Format_RGB888)
        self.label_error_img.setPixmap(QPixmap.fromImage(img_showed))

        # 保存异常帧
        isExists = os.path.exists(self.video_error_path)
        if (not isExists):
            os.makedirs(self.video_error_path)
        frame_saved = self.frame
        path = self.video_error_path + str(self.frame_index) + '.jpg'
        cv2.imencode('.jpg', frame_saved)[1].tofile(self.video_error_path + str(self.frame_index) + '.jpg')

        # 打标记
        self.init_bar_btn(path)

        # 日志输出、预警标签颜色改变、处理器异常还原
        self.log_info = "视频" + self.video_name + "第" + str(self.frame_index) + "帧出现异常 \n"
        self.label_is_error.setStyleSheet("background-color: red ")
        self.i_processor.is_error = False
        self.log()

    ## 日志输出，设置日志标签内容
    def log(self):
        pretxt = self.teb_log.toPlainText()
        self.teb_log.setText(pretxt + self.log_info)

    ## 正常状态，设置预警标签颜色
    def normal(self):
        self.label_is_error.setStyleSheet("background-color: rgb(20,155,20) ")

    def open_picture(self):
        # self.pic_url = QFileDialog.getOpenFileUrl()[0].url()[8:].replace('\\','/')
        self.pic_url = QFileDialog.getOpenFileName(self, "open file dialog")[0]
        # 打开标注图片窗口
        self.show_labeling_widget()

    def show_labeling_widget(self):
        self.labeling_ui = Ui_label_img.Ui_MainWindow(self.pic_url)
        self.labeling_ui.show()

    def init_bar_btn(self, url):
        # label init
        label = CustomProTagLabel(url)
        label.setParent(self)
        label.hide()
        # btn init
        cur_btn = CustomButton(label, url)
        cur_btn.setParent(self)
        self.bar_btn.append(cur_btn)
        self.bar_btn[-1].show()
        # set geo
        (x, y) = self.get_bar_btn_geo()
        cur_btn.setGeometry(x, y, 10, 20)
        label.setGeometry(x, y, 20, 20)

    def get_bar_btn_geo(self):
        x_offset = self.probar_load.value() * self.probar_load.width() / self.probar_load.maximum()
        y = self.probar_load.geometry().y() + self.probar_load.height() / 2
        x = self.probar_load.geometry().x() + x_offset
        return (x, y)

    def change_save_path(self):
        path = None
        if not self.init_path:
            while (path == None or path == ""):
                path = QFileDialog.getExistingDirectory(self, "请选择视频异常帧保存路径", r"./res")
            self.init_path = True
        else:
            path = QFileDialog.getExistingDirectory(self, "选择视频异常帧保存路径", self.dir_path)

        if path != "":
            self.dir_path = str(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainMindow = myMainWindow()
    mainMindow.show()
    sys.exit(app.exec_())
