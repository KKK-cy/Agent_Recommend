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

class GetEmotionJuzhen(object):
    def __init__(self,settings,database):
        self.settings = settings
        self.database = database

    # 根据中介-词语矩阵 和 评论文本情感分值 产生  中介-情感矩阵
    def ronghe_juzhen(self):
        # 1.获取中介-词语矩阵
        result = self.get_all_words(self.settings.fenci_result)
        # print("3.1 开始获取中介 - 词语矩阵")
        agent_df = self.get_agent_juzhen(self.settings.fenci_result, result, self.settings.top_k_words)
        # 2.融合推荐总得分形成中介-情感矩阵
        # print("3.2 开始拼接中介-情感矩阵")
        data = pd.read_csv(self.settings.recommend_score)
        recommend_df = pd.DataFrame(data, columns=["agent_id", "recommend_score"]).drop_duplicates()
        final_df = pd.merge(recommend_df, agent_df, on="agent_id")
        # print("3.3 拼接后得到的中介-情感矩阵为：%s" % final_df)
        print("产生中介-情感矩阵成功！")
        return final_df


    # 根据中介-情感矩阵计算中介之间的相似度，并保留k个邻居
    def get_similar(self,df):
        agent_list = df["agent_id"].tolist()
        final_result = pd.DataFrame(index=agent_list, columns=agent_list)
        # print("3.4 根据 中介-情感矩阵 计算中介两两之间的相似度，花费时间可能较长，请耐心等候哦")
        for loc1 in tqdm(range(len(agent_list))):
            for loc2 in range(len(agent_list)):
                if loc1 == loc2:
                    # 自身相似度置为0
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


    def get_k_neighbors(self,agent_list, df, neighbors):
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

    # 读取分词结果文件，统计所有词语的出现次数
    def get_all_words(self,fileinpath):
        # print("2.2 开始统计所有词语的出现次数")
        data = pd.read_csv(fileinpath)

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
        return result

    # 产生中介-词语矩阵
    def get_agent_juzhen(self,fileinpath, result, number):
        data = pd.read_csv(fileinpath)
        agent_id_list = list(set(data["agent_id"].tolist()))

        top_k_words_list = self.get_top_k_words(result, number)
        degree_words, degree_dict = self.settings.degreewordslist(self.settings.degree_in_path)
        no_words = self.settings.nowordslist(self.settings.no_in_path)

        for k_word in top_k_words_list:
            if k_word in degree_words:
                # print("%s在程度副词中，需要删除..." % k_word)
                top_k_words_list.remove(k_word)
            elif k_word in no_words:
                # print("%s在否定词中，需要删除..." % k_word)
                top_k_words_list.remove(k_word)
        print("最终产生的{num}个词语为{words}".format(num=len(top_k_words_list), words=top_k_words_list))

        all_agent_result = []
        for agent_id in agent_id_list:
            agent_result = {}
            agent_result = agent_result.fromkeys(top_k_words_list, 0)
            agent_data = data[data["agent_id"] == agent_id]
            agent_data_fenci = agent_data["seg_comment_result"].tolist()

            """获取该中介的所有评论中的分词的总个数"""
            word_total_number = 0
            for comment in agent_data_fenci:
                comment = str(comment)
                comment_word_list = comment.split(" ")
                word_total_number += len(comment_word_list)

            # 获取到前k个词每个词语在所有词语中的出现频率
            for comment in agent_data_fenci:
                comment = str(comment)
                comment_word_list = comment.split(" ")
                for word in comment_word_list:
                    if word in top_k_words_list:
                        agent_result[word] += round(1 / word_total_number, 3)
            agent_result["agent_id"] = agent_id
            all_agent_result.append(agent_result)

        top_k_words_list.append("agent_id")
        agent_df = pd.DataFrame(all_agent_result, columns=top_k_words_list)
        print("产生中介-词语矩阵成功！")
        return agent_df

    # 获取出现次数最高的前k个词语
    def get_top_k_words(self,result, degree_nums):
        # 前num个词语
        final_result = result[:(degree_nums)]
        top_k_words = {}
        for i in final_result:
            top_k_words[i[0]] = i[1]
        top_k_words_list = list(top_k_words.keys())
        # print("出现次数最高的前 %s 个词语为： %s " % (degree_nums, str(top_k_words_list)))
        return top_k_words_list
