# -*- coding: utf-8 -*-

"""
    # @Author : Administrator
    # @Time : 2020/4/21 22:49
    脚本说明：
        1. 根据首要推荐依据和次要推荐依据形成最终的推荐列表
        2. 根据推荐列表获取中介的详细信息，并写入结果展示界面
"""
import pandas as pd
from ..seetings import chuli_agent_other_information, html_path, recommend_number


def get_first_recom(fileinpath):
    recommend_list = [line.strip() for line in open(fileinpath, encoding='GBK').readlines()]
    return recommend_list


def get_second_recom(fileinpath):
    data = pd.read_csv(fileinpath)
    data = data.set_index("agent_id").T.to_dict("list")
    return data


def recommend(recommend_list, df, recommend_number):
    # print("7.3 推荐流程如下：")
    final_list = []
    for i in recommend_list:
        if len(final_list) < recommend_number:
            if i not in final_list:
                # print("    %s 不在推荐列表中，添加" % i)
                final_list.append(str(i))
                # 获取i的邻居并添加进推荐列表中
                neighbors = df[int(i)]
                neighbors = neighbors[0]
                neighbors = neighbors[:-1]
                neighbors = neighbors[1:]
                neighbors = neighbors.split(", ")
                # print("    %s 的邻居为：%s" % (i, neighbors))
                final_list.extend(neighbors)
                # 推荐列表去重
                final_list = list(set(final_list))
                # print("    将 %s 的邻居加入推荐列表并去重后为：%s" % (i, final_list))
            # else:
                # print("    %s 已在推荐列表中" % i)
        else:
            # print("    推荐个数 %s 已达到...即将退出推荐" % recommend_number)
            print("最终产生的推荐列表为 %s " % final_list)
            return final_list



