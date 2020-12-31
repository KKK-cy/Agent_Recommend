# -*- coding: utf-8 -*-

"""
    # @Author : Administrator
    # @Time : 2020/4/21 22:30
    脚本说明：
        1. 计算分类结果得到评论情感分值
        2. 对用户提问获取权重列表和要推荐的中介个数
        3. 融合权重矩阵计算最终推荐得分recommend_score
"""
import pandas as pd
from numpy import mean
from tqdm import tqdm

from ..seetings import chuli_agent_other_information, save_as_csv

"""计算每条评论的得分"""
def get_score(emotion_word, degree_word, no_word):
    score = 0
    if emotion_word:
        for i in emotion_word.keys():
            # print("情感词位置为：%s" % i)
            # 程度副词 & 否定词
            if i - 1 in degree_word.keys() and i - 2 in no_word.keys():
                # print("%s位置前有程度副词,位置在：%s，有否定词，位置在：%s" % (i,i-1,i-2))
                score += float(emotion_word[i]) * float(degree_word[i - 1]) * float(no_word[i - 2])
            # 只有程度副词
            elif i - 1 in degree_word.keys() and i - 2 not in no_word.keys():
                # print("%s位置前只有程度副词,位置在：%s" % (i,i-1))
                score += float(emotion_word[i]) * float(degree_word[i - 1])
            # 只有否定词
            elif i - 1 not in degree_word.keys() and i - 2 in no_word.keys():
                # print("%s位置前只有否定词,位置在：%s" % (i,i-2))
                score += float(emotion_word[i]) * float(no_word[i - 2])
            # 程度副词和否定词都没有
            else:
                score += float(emotion_word[i])
        return score
    else:
        return score


# 对用户提问，达到个性化推荐
def get_quanzhong_w(w = [0.2, 0.5, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]):
    print("------------ 对用户进行个性化提问，根据用户的回答设置不同的权重 ---------------")
    print("权重列表w的初始值为：%s，其中用户评分所占比重为：%.2f，评论文本情感得分值所占比重为：%.2f，"
          "服务年限所占比重为：%.2f，平均每年买卖成交量所占比重为：%.2f，平均每年租赁成交量所占比重为：%.2f，"
          "30天看房数量所占比重为：%.2f，关注人数所占比重为：%.2f，标签平均占比所占比重为：%.2f" % (w, w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7]))

    print("提问1：请问您最近需要租房还是买卖房？租房请输入1，买卖房请输入2")
    answer_1 = int(input())
    if answer_1 == 1:
        w[3], w[4] = 0.1, 0
    else:
        w[4], w[3] = 0.1, 0

    print("提问2：请问您比较偏向关注人数多的中介还是带看房次数多的中介？关注人数多的中介请输入1，带看房次数多的中介请输入2，两者均偏向请输入3")
    answer_2 = int(input())
    if answer_2 == 1:
        w[6], w[5] = 0.1, 0
    elif answer_2 == 2:
        w[5], w[6] = 0.1, 0
    else:
        w[5], w[6] = 0.05, 0.05

    print("权重参数调整后的最终权重列表w为：%s" % w)
    print("提问3：请问你想要被推荐几个中介？")
    recommend_number = int(input())

    return w,recommend_number

def get_emotion_score(fileinpath, fileoutpath, w):
    agent_info_df = pd.read_csv(fileinpath)
    agent_list = list(set(list(agent_info_df["agent_id"])))
    final_result_df = pd.DataFrame()
    for agent_id in tqdm(agent_list):
        # print("%s 的评论中的情感分值计算即将开始..." % str(agent_id))
        agent_df = agent_info_df.loc[agent_info_df["agent_id"] == agent_id]
        agent_star_score = agent_df["star_score"].tolist()
        # print("该中介的评论有%s条" % str(len(agent_df)))
        agent_df_emotion = agent_df["emotion_words"].tolist()
        agent_df_degree = agent_df["degree_words"].tolist()
        agent_df_no = agent_df["no_words"].tolist()
        score_list = []
        for loc in range(len(agent_df)):
            emotion_word = eval(agent_df_emotion[loc])
            degree_word = eval(agent_df_degree[loc])
            no_word = eval(agent_df_no[loc])
            score = get_score(emotion_word, degree_word, no_word)
            # print("第%s个评论的情感分值为：%s" % (loc+1,score))
            score_list.append(score)
        # 计算平均值并与评分进行加权求和并保留5位小数
        average_score = round(mean(score_list), 5)
        average_star_score = round(mean(agent_star_score), 5)

        # 获取推荐总得分(多维度推荐)
        recommend_score = get_recommend_score(chuli_agent_other_information, agent_id, average_star_score,
                                              average_score, w)
        # print("ID为%s的中介经过评分与情感分数加权求和后的最终推荐得分为：%s" % (agent_id,recommend_score))
        agent_df["emotion_score"] = score_list
        agent_df["recommend_score"] = recommend_score
        final_result_df = final_result_df.append(agent_df)
    save_as_csv(final_result_df, fileoutpath)

# 多维度推荐得到recommend_score
# 原始评分（w[0]） 评论文本情感得分平均值(w[1]) 服务年限(w[2]) 平均每年卖房数量(w[3]) 平均每年租房数量(w[4]) 30天内带看房次数(w[5]) 关注人数(w[6]) 平均标签占比(w[7])
def get_recommend_score(chuli_agent_other_information, agent_id, star_score, emotion_score, w):
    # 获取其它的维度
    other_data = pd.read_csv(chuli_agent_other_information)
    other_data = pd.DataFrame(other_data, columns=["agent_id", "agent_name", "service_year", "sale_num_every_year",
                                                   "rent_num_every_year", "kanfang_number_30_days", "followers_number", "avg_biaoqian_percent"])
    agent_df = other_data[other_data["agent_id"] == agent_id]
    agent_dict = agent_df.set_index("agent_id").to_dict("list")
    score = w[0] * star_score + w[1] * emotion_score + w[2] * agent_dict["service_year"][0] + w[3] * agent_dict["sale_num_every_year"][
        0] + w[4] * agent_dict["rent_num_every_year"][0] + w[5] * agent_dict["kanfang_number_30_days"][0] + w[6] * agent_dict["followers_number"][0] + \
            w[7] * agent_dict["avg_biaoqian_percent"][0]
    return score

# 根据recommend_score排序形成首要推荐依据并存储
def recom_first(fileinpath, fileoutpath):
    data = pd.read_csv(fileinpath)
    recommend_df = pd.DataFrame(data, columns=["agent_id", "recommend_score"]).drop_duplicates()
    # 根据推荐得分排序形成首要推荐依据
    recommend_df_new = recommend_df.sort_values(by="recommend_score", ascending=False)
    # print("排序后，推荐得分由高到低为：%s" % recommend_df_new)
    # print("排序后的推荐顺序为：%s" % recommend_df_new["Agent ID"].tolist())
    # 写入txt文件
    f = open(fileoutpath, "w")
    for line in recommend_df_new["agent_id"].tolist():
        f.writelines(str(line) + "\n")

