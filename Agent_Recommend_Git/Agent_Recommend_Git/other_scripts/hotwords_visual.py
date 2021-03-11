# -*- coding:utf-8 -*-
# @Time : 2021/3/11 11:22
# @Author : KCY
# @File : hotwords_visual.py
# @Software: PyCharm

import pandas as pd
import numpy as np
from tqdm import tqdm
# 导入扩展库
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class HotwordsVisual(object):
    def __init__(self, settings, database):
        self.settings = settings
        self.database = database

    # 获取出现次数最高的前N个词语，产生词云图片
    def hotwords_ciyun(self, fenci_result_df):
        # 获取所有词语的出现次数
        result,all_words_times = self.get_all_words(fenci_result_df)
        top_k_words_list = self.get_top_k_words(result, self.settings.top_k_words)
        # 从热门词语中去除否定词、程度副词等无意义的词语
        degree_words, degree_dict = self.settings.degreewordslist(self.settings.degree_in_path)
        no_words = self.settings.nowordslist(self.settings.no_in_path)
        for k_word in top_k_words_list:
            if k_word in degree_words:
                top_k_words_list.remove(k_word)
            elif k_word in no_words:
                top_k_words_list.remove(k_word)

        # 根据所有词语出现次数字典result出现次数最高的前K个词语列表top_k_words_list产生新字典，用来记录前K个词语和对应的出现次数
        top_k_words_dict = {}
        for top_k_words in top_k_words_list:
            top_k_words_dict[top_k_words] = all_words_times[top_k_words]

        return top_k_words_dict

    # 读取分词结果文件，统计所有词语的出现次数
    def get_all_words(self, fenci_result_df):
        # print("2.2 开始统计所有词语的出现次数")
        data = fenci_result_df

        fenci_result_df = data["seg_comment_result"]
        comments_word_list = fenci_result_df.tolist()
        all_words = []
        all_words_times = {}
        for comment_word in comments_word_list:
            comment_word = str(comment_word)
            # 将每条评论中的分词结果变为列表形式
            comment_word_list = comment_word.split(" ")
            for word in comment_word_list:
                if word not in all_words and word != "":
                    all_words.append(word)
        # print("共有 %d 个词语" % len(all_words), end=" ,")

        # 将所有词语转化为字典，初始值给0
        all_words_times = all_words_times.fromkeys(all_words, 0)
        # 遍历每条评论，获取到词语出现的总次数
        for comment_word in comments_word_list:
            comment_word = str(comment_word)
            # 将每条评论中的分词结果变为列表形式
            comment_word_list = comment_word.split(" ")
            for word in comment_word_list:
                if word in all_words_times.keys():
                    all_words_times[word] += 1
        result = sorted(all_words_times.items(), key=lambda x: x[1], reverse=True)
        # print("所有词语的出现总次数由高到低排序为：%s " % result)
        return result,all_words_times

    # 获取出现次数最高的前k个词语
    def get_top_k_words(self, result, degree_nums):
        # 前num个词语
        final_result = result[:(degree_nums)]
        top_k_words = {}
        for i in final_result:
            top_k_words[i[0]] = i[1]
        top_k_words_list = list(top_k_words.keys())
        # print("出现次数最高的前 %s 个词语为： %s " % (degree_nums, str(top_k_words_list)))
        return top_k_words_list