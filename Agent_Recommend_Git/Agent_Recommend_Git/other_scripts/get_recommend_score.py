# -*- coding:utf-8 -*-
# @Time : 2021/1/7 15:23
# @Author : KCY
# @Software: PyCharm

import pandas as pd
from tqdm import tqdm

"""
    从最终结果表中获取到所需的数据，根据传入的w计算推荐总得分，形成首要推荐依据
"""

class GetRecommendScore(object):
    def __init__(self,settings,database):
        self.settings = settings
        self.database = database

    def get_recommend_score(self, final_result_df,w):
        agent_info_df = final_result_df
        agent_list = list(set(list(agent_info_df["agent_id"])))
        final_result_df = pd.DataFrame()
        for agent_id in tqdm(agent_list):
            agent_df = agent_info_df.loc[agent_info_df["agent_id"] == agent_id]

            agent_df["recommend_score"] = round(w[0] * float(agent_df["average_star_score"]) + w[1] * float(
                agent_df["average_emotion_score"])
            + w[2] * int(agent_df["service_year"]) + w[3] * float(agent_df["sale_num_every_year"])
            + w[4] * float(agent_df["rent_num_every_year"]) + w[5] * int(agent_df["kanfang_number_30_days"])
            + w[6] * int(agent_df["followers_number"]) + w[7] * float(agent_df["avg_biaoqian_percent"]),5)

            # 输出一下计算公式
            # if agent_id == 610604:
            #     print("""
            #     {agent_id}的推荐总得分计算公式为：
            #     {w0}*{average_star_score}+{w1}*{average_emotion_score}+{w2}*{service_year}+{w3}*{sale_num_every_year}+{w4}*{rent_num_every_year}
            #     +{w5}*{kanfang_number_30_days}+{w6}*{followers_number}+{w7}*{avg_biaoqian_percent}
            #     """.format(agent_id=agent_id,w0=w[0],w1=w[1],w2=w[2],w3=w[3],w4=w[4],w5=w[5],w6=w[6],w7=w[7],
            #                average_star_score=float(agent_df["average_star_score"]),average_emotion_score=float(agent_df["average_emotion_score"]),
            #                service_year=int(agent_df["service_year"]),sale_num_every_year=float(agent_df["sale_num_every_year"]),
            #                rent_num_every_year=float(agent_df["rent_num_every_year"]),kanfang_number_30_days=int(agent_df["kanfang_number_30_days"]),
            #                followers_number=int(agent_df["followers_number"]),avg_biaoqian_percent=float(agent_df["avg_biaoqian_percent"]),))
            final_result_df = final_result_df.append(agent_df)

        # 只保留中介ID、姓名、推荐总得分3列
        final_result_df = final_result_df[["agent_id","agent_name","recommend_score"]]
        return final_result_df

    # 根据recommend_score排序形成首要推荐依据并存储
    def recom_first(self,recommend_score_df, fileoutpath):
        data = recommend_score_df
        recommend_df = pd.DataFrame(data, columns=["agent_id", "recommend_score"]).drop_duplicates()
        # 根据推荐得分排序形成首要推荐依据
        recommend_df_new = recommend_df.sort_values(by="recommend_score", ascending=False)
        # print("排序后，推荐得分由高到低为：%s" % recommend_df_new)
        # print("排序后的推荐顺序为：%s" % recommend_df_new["Agent ID"].tolist())
        # 写入txt文件
        f = open(fileoutpath, "w")
        for line in recommend_df_new["agent_id"].tolist():
            f.writelines(str(line) + "\n")

