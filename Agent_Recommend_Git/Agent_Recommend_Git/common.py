# -*- coding:utf-8 -*-
# @Time : 2021/1/7 15:25
# @Author : KCY
# @File : common.py
# @Software: PyCharm

"""
    参数配置文件
"""
import os
import pandas as pd

class Common(object):
    def __init__(self):
        # 首要推荐依据
        self.recommend_first = "Agent_Recommend_Git/data/result/recommend_first.txt"
        # 次要推荐依据
        self.recommend_second = "Agent_Recommend_Git/data/result/recommend_second.csv"

        # 产生中介-词语矩阵的出现次数最高的前10个词
        self.top_k_words = 12
        # 保留的邻居个数
        self.neighbors = 3
        # 初始权重列表
        self.w = [0.6,0.2,0.05,0.05,0.05,0.05,0.05,0.05]

        # 词典
        self.stopwords_in_path = "Agent_Recommend_Git/data/cidian/stopwords_chuli.txt"
        self.emotion_in_path = "Agent_Recommend_Git/data/cidian/emotion_words.xlsx"
        self.no_in_path = "Agent_Recommend_Git/data/cidian/no_words.txt"
        self.degree_in_path = "Agent_Recommend_Git/data/cidian/degree_word.xlsx"

    # 一些公用函数
    def save_as_csv(self,df, fileoutpath):
        if os.path.exists(fileoutpath):
            print("[ 文件已存在,将删除重写 ]")
            os.remove(fileoutpath)
            df.to_csv(fileoutpath, mode='a+', index=False, encoding="utf-8")
        else:
            print('[ 文件不存在，将创建 ]')
            df.to_csv(fileoutpath, index=False, encoding="utf-8")

    def emotionwordslist(self,fileinpath):
        emotion_data = pd.read_excel(fileinpath)
        emotionwords = emotion_data["word"].tolist()
        emotion_dict = emotion_data.set_index("word").to_dict()["value"]
        return emotionwords, emotion_dict

    """ 获取正负情感词列表 """
    def zheng_fu_emotion_words(self,fileinpath):
        emotion_data = pd.read_excel(fileinpath)
        zheng_emotionwords = emotion_data[emotion_data["type"]=="P"]
        fu_emotionwords = emotion_data[emotion_data["type"]=="N"]

        zhengwords = zheng_emotionwords["word"].tolist()
        fuwords = fu_emotionwords["word"].tolist()
        print("正向情感词有%s个，负向情感词有%s个" % (len(zhengwords),len(fuwords)))
        return zhengwords,fuwords

    def degreewordslist(self,fileinpath):
        degree_data = pd.read_excel(fileinpath)
        degree_words = degree_data["word"].tolist()
        degree_dict = degree_data.set_index("word").to_dict()["value"]
        return degree_words, degree_dict


    def nowordslist(self,fileinpath):
        nowords = [line.strip() for line in open(fileinpath, encoding='GBK').readlines()]
        return nowords


    def stopwordslist(self,fileinpath):
        stopwords = [line.strip() for line in open(fileinpath, encoding='GBK').readlines()]
        return stopwords

