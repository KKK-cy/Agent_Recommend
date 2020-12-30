# -*- coding: utf-8 -*-

"""
    # @Author : Administrator
    # @Time : 2020/4/14 21:18
    脚本说明：
        程序中所有用到的变量和公共函数
"""

import os
import pandas as pd
import sqlalchemy
import warnings
warnings.filterwarnings("ignore")

# 评论中字符的最少个数
min_comment_zifu = 3
# 出现次数最高的前250个词，从中手动筛选出常见的程度副词并给定权值
degree_nums = 250
# 产生中介-词语矩阵的出现次数最高的前10个词
top_k_words = 12
# 每个中介要保留的邻居个数
neighbors = 3
# 权重值矩阵，依次是：【评分  情感得分值  服务年限、买卖成交、租赁成交、30天看房数量、关注人数和标签平均占百分比】
w = [0.2, 0.5, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
# 最终推荐个数,初始化为5
recommend_number = 5

""" 数据库相关信息 """
database_name = "agent_recommend"
""" 处理后的评论存储表 """
agent_comments_table = "agent_comments"
""" 处理后的其他信息存储表 """
agent_other_info_table = "agent_other_information"
# 存储中间结果的一些表
zhongjian_recommend_score_table = "recommend_score"


"""一些文件存储路径"""
""" 中介源ID列表 """
agent_ids = 'Agent_Recommend_Git/agent_infors/agentIDs.xlsx'
""" 爬取到的中介评论文件 """
agent_comments = 'Agent_Recommend_Git/agent_infors/AgentComments.csv'
""" 爬取到的中介其他信息文件 """
agent_other_information = 'Agent_Recommend_Git/agent_infors/AgentOtherInfor.csv'

# 处理后的中介评论文件
chuli_agent_comments = "Agent_Recommend_Git/agent_infors/chuli_AgentComments.csv"
# 处理后的中介其他信息文件
chuli_agent_other_information = "Agent_Recommend_Git/agent_infors/chuli_AgentOtherInfor.csv"

# 分词结果文件
fenci_result = "Agent_Recommend_Git/data/result/comments_fenci.csv"
# 根据前250个词语产生常见的程度副词词典
top_250_word_path = "Agent_Recommend_Git/data/result/top_250.txt"
# 分词结果分类为情感词、程度副词、否定词文件
fenci_result_fenlei = "Agent_Recommend_Git/data/result/emotion_degree_no_words.csv"
# 存储推荐总得分文件
recommend_score = "Agent_Recommend_Git/data/result/recommend_score.csv"

# 首要推荐依据
recommend_first = "Agent_Recommend_Git/data/result/recommend_yiju/recommend_first.txt"
# 次要推荐依据
recommend_second = "Agent_Recommend_Git/data/result/recommend_yiju/recommend_second.csv"

# 相关的词典文件
stopwords_in_path = "Agent_Recommend_Git/data/cidian/stopwords_chuli.txt"
emotion_in_path = "Agent_Recommend_Git/data/cidian/emotion_words.xlsx"
degree_in_path = "Agent_Recommend_Git/data/cidian/degree_word.xlsx"
no_in_path = "Agent_Recommend_Git/data/cidian/no_words.txt"

# 一些公用函数
def save_as_csv(df, fileoutpath):
    if os.path.exists(fileoutpath):
        print("[ 文件已存在,将删除重写 ]", end=" ,")
        os.remove(fileoutpath)
        df.to_csv(fileoutpath, mode='a+', index=False, encoding="utf-8")
    else:
        print('[ 文件不存在，将创建 ]', end=" ,")
        df.to_csv(fileoutpath, index=False, encoding="utf-8")


def emotionwordslist(fileinpath):
    emotion_data = pd.read_excel(fileinpath)
    emotionwords = emotion_data["word"].tolist()
    emotion_dict = emotion_data.set_index("word").to_dict()["value"]
    return emotionwords, emotion_dict


def degreewordslist(fileinpath):
    degree_data = pd.read_excel(fileinpath)
    degree_words = degree_data["word"].tolist()
    degree_dict = degree_data.set_index("word").to_dict()["value"]
    return degree_words, degree_dict


def nowordslist(fileinpath):
    nowords = [line.strip() for line in open(fileinpath, encoding='GBK').readlines()]
    return nowords


def stopwordslist(fileinpath):
    stopwords = [line.strip() for line in open(fileinpath, encoding='GBK').readlines()]
    return stopwords


""" 将某个文件中的所有数据写入至数据库的某个表中 """


def get_engine(database_name):
    return sqlalchemy.create_engine("mysql+pymysql://root:1@localhost:3306/" + database_name)


def csv_to_database(engine, file_name, database_name, table_name):
    df = pd.read_csv(file_name)
    try:
        df.to_sql(table_name, engine, index=False)
        print("    %s 文件已写入数据库 %s 的 %s 表中" % (file_name, database_name, table_name))
    except ValueError:
        print("    %s 表在数据库 %s 中已存在" % (table_name, database_name), end="   ,")
        engine.execute("drop table if exists %s" % table_name)
        print("    %s 表已删除，即将重新写入数据..." % table_name, end="    ,")
        df.to_sql(table_name, engine, index=False)
        print("    %s 文件已写入数据库 %s 的 %s 表中" % (file_name, database_name, table_name))
