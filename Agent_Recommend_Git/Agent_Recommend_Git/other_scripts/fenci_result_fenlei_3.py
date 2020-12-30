# -*- coding: utf-8 -*-

"""
    # @Author : Administrator
    # @Time : 2020/4/21 22:27
    脚本说明：
        对分词结果进行分类
"""
from tqdm import tqdm

from ..seetings import emotionwordslist, emotion_in_path, degreewordslist, degree_in_path, nowordslist, no_in_path, \
    save_as_csv
import pandas as pd

# 对分词结果进行分类
def seg_result_emotionwords(fileinpath, fileoutpath):
    agent_info_df = pd.read_csv(fileinpath)
    # 情感词典列表
    emotion_words_list, emotion_dict = emotionwordslist(emotion_in_path)
    degree_words_list, degree_dict = degreewordslist(degree_in_path)
    no_words_list = nowordslist(no_in_path)
    # 最终结果
    final_result_df = pd.DataFrame()
    agent_list = list(set(list(agent_info_df["agent_id"])))

    """对于每个中介，获取到它的分词结果列表并对其中的词语进行判断"""
    for agent_id in tqdm(agent_list):
        agent_df = agent_info_df.loc[agent_info_df["agent_id"] == agent_id]
        # print("该中介的评论有%s条" % str(len(agent_df)))
        agent_df["emotion_words"] = ""
        agent_df["degree_words"] = ""
        agent_df["no_words"] = ""

        agent_emotion_words_list = []
        agent_degree_words_list = []
        agent_no_words_list = []

        for seg_result in agent_df["seg_comment_result"]:
            emotion_words = {}
            degree_words = {}
            no_words = {}
            # print("要划分的分词结果为 %s" % seg_result)
            seg_result = str(seg_result)
            seg_result = seg_result.split()

            """循环每条分词结果中的每个词语，判断是否是情感词 {位置：情感强度值}"""
            for loc in range(len(seg_result)):
                if seg_result[loc] in emotion_words_list:
                    emotion_words[loc] = emotion_dict[seg_result[loc]]
                elif seg_result[loc] in degree_words_list:
                    degree_words[loc] = degree_dict[seg_result[loc]]
                elif seg_result[loc] in no_words_list:
                    no_words[loc] = "-1"
            # 将该条评论中的3类词以字符串的形式存到该中介的所有评论列表中
            agent_emotion_words_list.append(emotion_words)
            agent_degree_words_list.append(degree_words)
            agent_no_words_list.append(no_words)

        agent_df["emotion_words"] = agent_emotion_words_list
        agent_df["degree_words"] = agent_degree_words_list
        agent_df["no_words"] = agent_no_words_list

        final_result_df = final_result_df.append(agent_df, sort=False)

    save_as_csv(final_result_df, fileoutpath)
    print("分词结果分类成功!")
