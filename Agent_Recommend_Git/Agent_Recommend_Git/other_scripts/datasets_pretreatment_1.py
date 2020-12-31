# -*- coding: utf-8 -*-
import pandas as pd
from tqdm import tqdm
from ..seetings import min_comment_zifu, save_as_csv, get_engine, database_name, csv_to_database, chuli_agent_comments, \
    agent_comments_table, chuli_agent_other_information, agent_other_info_table

"""
    脚本说明：预处理脚本
    1.预处理中介评论文件：
        - 去除字数<3的评论
        - 删除重复评论
        - 去除评论中的特殊字符
    2.预处理中介其它信息文件
        - 将各个标签的数量转换为各个标签占评论总条数的百分比，并计算出全部6个标签的平均占比
        - 将买卖房屋和租赁房屋量 除以 服务年限，转换为平均每年买卖房屋数量和平均每年租赁房屋数量
    3.将预处理后的数据写入数据库
"""

# 根据中介ID获取该中介的所有评论
def comment_filter(df, agentID):
    # 1.读出文件中某个中介的全部评论
    df1 = df[df['agent_id'].isin([agentID])]
    # 2.删除字数小于3的评论
    df2 = df1[df1['comment'].map(len) > min_comment_zifu]
    # 3.删除其中的重复评论
    df3 = df2.drop_duplicates()
    # 4.去除评论中的特殊字符
    df3["comment"] = df3["comment"].map(
        lambda x: x.replace("▢▢", " ").replace("（｡ò ∀ ó｡）", " ").replace("(✪▽✪)", " ").replace("(*￣m￣)", " ").replace(
            "□□", " ").replace("^_^", " ").replace("❤", " ").replace("⛱", " ").replace("(*๓´╰╯`๓)♡", " ").replace(
            "️", " ").replace("▢", " ").replace("•", " ").replace("(ง •̀_•́)ง", " "))
    return df3

# 处理中介评论数据
def comment_chuli(agent_comments, chuli_agent_comments):
    data = pd.read_csv(agent_comments, dtype=str)
    df = data.fillna('')
    agent_list = list(set(df["agent_id"].tolist()))
    final_result = pd.DataFrame(columns=df.columns)
    for zhongjieID in tqdm(agent_list):
        agent_df = comment_filter(df, zhongjieID)
        final_result = final_result.append(agent_df)
    save_as_csv(final_result, chuli_agent_comments)
    print("中介评论文件处理成功！处理前有评论<{num1}>条，处理后剩余<{num2}>条".format(num1=len(df),num2=len(final_result)))

# 处理中介其他信息数据
def other_chuli(agent_other_information, chuli_agent_other_information):
    data = pd.read_csv(agent_other_information)

    data["sale_num_every_year"] = data[["sale_number", "service_year"]].apply(lambda x: round(x["sale_number"] / x["service_year"], 5), axis=1)
    data["rent_num_every_year"] = data[["rent_number", "service_year"]].apply(lambda x: round(x["rent_number"] / x["service_year"], 5), axis=1)

    data["on_time_percent"] = data[["on_time", "comments_number"]].apply(lambda x: round(x["on_time"] / x["comments_number"], 5), axis=1)
    data["walking_map_percent"] = data[["walking_map", "comments_number"]].apply(lambda x: round(x["walking_map"] / x["comments_number"], 5), axis=1)
    data["good_service_percent"] = data[["good_service", "comments_number"]].apply(lambda x: round(x["good_service"] / x["comments_number"], 5), axis=1)
    data["positive_energy_percent"] = data[["positive_energy", "comments_number"]].apply(lambda x: round(x["positive_energy"] / x["comments_number"], 5), axis=1)
    data["warm_heart_percent"] = data[["warm_heart", "comments_number"]].apply(lambda x: round(x["warm_heart"] / x["comments_number"], 5), axis=1)
    data["professional_work_percent"] = data[["professional_work", "comments_number"]].apply(lambda x: round(x["professional_work"] / x["comments_number"], 5), axis=1)
    data["avg_biaoqian_percent"] = data[["on_time_percent", "walking_map_percent", "good_service_percent", "positive_energy_percent", "warm_heart_percent", "professional_work_percent"]].apply(
        lambda x: round((x["on_time_percent"] + x["walking_map_percent"] + x["good_service_percent"] + x["positive_energy_percent"] + x["warm_heart_percent"] + x["professional_work_percent"]) / 6, 5), axis=1)
    data['agent_img'] = ['https://image.5i5j.com/picture/%i.jpg' % i for i in data['agent_id']]
    save_as_csv(data, chuli_agent_other_information)
    print("中介其它信息文件处理成功！")

# 将预处理后的结果写入数据库
def pre_result_to_database(engine):
    print("1.3 将处理后的数据写入数据库对应的表中")
    # 根据传入的文件名、数据库名、表名将csv文件写入数据库的对应表中
    csv_to_database(engine, chuli_agent_comments, database_name, agent_comments_table)
    csv_to_database(engine, chuli_agent_other_information, database_name, agent_other_info_table)
    print("处理后的数据存入数据库成功！")