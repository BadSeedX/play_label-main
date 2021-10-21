import cv2
import numpy as np
import os

class img_processor:
    ## 初始化
    def __init__(self):
        self.is_error = False
        self.standard_list = ['/Source/standard_1.jpg', '/Source/standard_2.jpg', '/Source/standard_3.jpg', '/Source/standard_4.jpg']
        self.threshold_dic = {}
        self.init_standard_dis()
        

    ## 标准帧初始化
    def init_standard_dis(self):
        # 对每个标准帧计算三个哈希值
        self.pHash_standard = []
        self.aHash_standard = []
        self.dHash_standard = []
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\','/')
        for i in range(len(self.standard_list)):
            standard_frame = cv2.imdecode(np.fromfile(path + self.standard_list[i],dtype=np.uint8),cv2.IMREAD_COLOR)
            self.pHash_standard.append(self.pHash(standard_frame))
            self.aHash_standard.append(self.aHash(standard_frame))
            self.dHash_standard.append(self.dHash(standard_frame))
        
        # 标准帧阈值（min，max）
        self.threshold_dic[0] = [0.9296874, 0.9361980]
        self.threshold_dic[1] = [0.92578124, 0.9361980]
        self.threshold_dic[2] = [0.97135416, 0.9856771]
        self.threshold_dic[3] = [0.9687499, 0.9830730]


    ## 阈值判断
    def is_in_threshold(self, i, score):
        return score > self.threshold_dic[i][0] and score < self.threshold_dic[i][1]


    ## 海明距离计算
    def hammingDist(self, HASH_Standard, HASH_Temp):
        assert len(HASH_Standard) == len(HASH_Temp)
        return sum([ch1 != ch2 for ch1, ch2 in zip(HASH_Standard, HASH_Temp)])


    ## aHash计算
    def aHash(self, frame):
        frame = cv2.resize(frame, (8, 8), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        s = 0
        hash_str = ''
        for i in range(8):
            for j in range(8):
                s = s+gray[i,j]
        avg = s/64
        for i in range(8):
            for j in range(8):
                if gray[i,j] > avg:
                    hash_str = hash_str+'1'
                else:
                    hash_str = hash_str+'0'
        return hash_str


    ## dHash计算
    def dHash(self, frame):
        frame = cv2.resize(frame,(9,8),interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        hash_str = ''
        for i in range(8):
            for j in range(8):
                if gray[i, j] > gray[i, j+1]:
                    hash_str = hash_str+'1'
                else:
                    hash_str = hash_str+'0'
        return hash_str


    ## pHash计算
    def pHash(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, (64, 64), interpolation=cv2.INTER_CUBIC)
        h, w = frame.shape[:2]
        vis0 = np.zeros((h, w), np.float32)
        vis0[:h, :w] = frame
        vis1 = cv2.dct(cv2.dct(vis0))
        vis1.resize(32, 32)
        img_list = [y for x in vis1.tolist() for y in x]
        avg = sum(img_list)*1./len(img_list)
        avg_list = ['0' if i < avg else '1' for i in img_list]
        return ''.join(['%x' % int(''.join(avg_list[x:x + 4]), 2) for x in range(0, 32 * 32, 4)])


    ## 处理传入帧
    def process(self, frame):
        self.cur_frame = frame
        self.is_error = False
        self.similarity_compare()


    ## 相似度对比
    def similarity_compare(self):
        # 对传入的帧计算a、p、d哈希值
        cur_frame_score = {}
        cur_frame_score['pHash'] = self.pHash(self.cur_frame)
        cur_frame_score['aHash'] = self.aHash(self.cur_frame)
        cur_frame_score['dHash'] = self.dHash(self.cur_frame)
        out_score = []
        # 计算所得哈希值与标准帧的海明距离
        for i in range(len(self.standard_list)):
            score_p = 1 - self.hammingDist(self.pHash_standard[i], cur_frame_score['pHash'])* 1. / (32 * 32 / 4)
            score_a = 1 - self.hammingDist(self.aHash_standard[i], cur_frame_score['aHash'])* 1. / (32 * 32 / 4)
            score_d = 1 - self.hammingDist(self.dHash_standard[i], cur_frame_score['dHash'])* 1. / (32 * 32 / 4)
            # 取平均值作为当前帧相对于标准帧i的分数
            out_score.append((score_p + score_a + score_d)/3)
        # 阈值判断，若分数同时在所有标准帧的阈值内则有异常出现，is_error = True,否则为False
        is_error = True
        for i in range(len(self.standard_list)):
            if not self.is_in_threshold(i,out_score[i]):
                is_error = False
        self.is_error = is_error

