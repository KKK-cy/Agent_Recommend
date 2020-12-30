# -*- coding: utf-8 -*-

"""
    # @Author : Administrator
    # @Time : 2020/4/21 22:43
    脚本说明：
        1. 获得中介-词语矩阵
        2. 融合recommend_score形成中介-情感矩阵
        3. 计算相似度，保留邻居集
"""
import pandas as pd
import numpy as np
from tqdm import tqdm
from ..other_scripts.get_degree_words_2 import get_all_words, get_agent_juzhen
from ..seetings import fenci_result, top_k_words, recommend_score

# 根据中介-词语矩阵 和 评论文本情感分值 产生  中介-情感矩阵
def ronghe_juzhen():
    # 1.获取中介-词语矩阵
    result = get_all_words(fenci_result)
    # print("3.1 开始获取中介 - 词语矩阵")
    agent_df = get_agent_juzhen(fenci_result, result, top_k_words)
    # 2.融合推荐总得分形成中介-情感矩阵
    # print("3.2 开始拼接中介-情感矩阵")
    data = pd.read_csv(recommend_score)
    recommend_df = pd.DataFrame(data, columns=["agent_id", "recommend_score"]).drop_duplicates()
    final_df = pd.merge(recommend_df, agent_df, on="agent_id")
    # print("3.3 拼接后得到的中介-情感矩阵为：%s" % final_df)
    print("产生中介-情感矩阵成功！")
    return final_df


# 根据中介-情感矩阵计算中介之间的相似度，并保留k个邻居
def get_similar(df):
    agent_list = df["agent_id"].tolist()
    final_result = pd.DataFrame(index=agent_list, columns=agent_list)
    # print("3.4 根据 中介-情感矩阵 计算中介两两之间的相似度，花费时间可能较长，请耐心等候哦")
    for loc1 in tqdm(range(len(agent_list))):
        for loc2 in range(len(agent_list)):
            if loc1 == loc2:
                # print("%s与自身的相似度默认为1" % agent_list[loc1])
                dist = 0
                final_result.iloc[loc1, loc2] = dist
            else:
                p = df[df["agent_id"] == agent_list[loc1]]
                p = p.drop("agent_id", axis=1)
                p = np.array(p)
                q = df[df["agent_id"] == agent_list[loc2]]
                q = q.drop("agent_id", axis=1)
                q = np.array(q)
                # print("开始计算%s和%s的相似度..." % (agent_list[loc1],agent_list[loc2]))
                dist = round(np.linalg.norm(p - q), 5)
                # print("%s和%s的相似度为：%s" % (agent_list[loc1],agent_list[loc2],dist))
                final_result.iloc[loc1, loc2] = dist
    print("中介相似度矩阵计算完毕")
    return agent_list, final_result


def get_k_neighbors(agent_list, df, neighbors):
    # print("3.5 根据相似度高低获取中介的邻居集")
    result = []
    for agent_id in tqdm(agent_list):
        agent_info_df = df[agent_id]
        agent_info_dict = agent_info_df.to_dict()
        final_result = []
        sorted_agent = sorted([(k, v) for k, v in agent_info_dict.items()], reverse=True)
        tmp_set = set()
        for item in sorted_agent:
            tmp_set.add(item[1])
        for list_item in sorted(tmp_set, reverse=True)[:neighbors]:
            for dict_item in sorted_agent:
                if dict_item[1] == list_item:
                    final_result.append(dict_item[0])
        b = {}
        b["agent_id"] = agent_id
        b["Neighbors"] = final_result
        result.append(b)

    result = pd.DataFrame(result, columns=["agent_id", "Neighbors"])
    print("中介邻居集获取完毕")
    return result
