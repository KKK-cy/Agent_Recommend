from django.http import HttpResponse
from django.shortcuts import render

from Agent_Recommend_Git.other_scripts.agent_emotion_juzhen_5 import ronghe_juzhen, get_similar, get_k_neighbors
from Agent_Recommend_Git.other_scripts.fenci_result_fenlei_3 import seg_result_emotionwords
from Agent_Recommend_Git.other_scripts.get_recommend_score_4 import get_emotion_score, recom_first
from Agent_Recommend_Git.other_scripts.recommend_way_6 import get_first_recom, get_second_recom, recommend
from recommend_app.models import Agents_other_info

from Agent_Recommend_Git.seetings import w, fenci_result, fenci_result_fenlei, recommend_score, csv_to_database, \
    database_name, zhongjian_recommend_score_table, recommend_first,recommend_second, get_engine, neighbors
import warnings
warnings.filterwarnings("ignore")
""" 
主页：显示部分中介的名片卡 
"""


def home(request):
    agent_infos = Agents_other_info.objects.all()[:24]
    return render(request, 'home.html', {'agent_infos': agent_infos})


# 显示注册页面
def showwenjuan(request):
    return render(request, 'wenjuan.html')


# 获取注册时提交的数据
def wenjuan(request):
    # 获取买卖房屋还是租赁房屋
    answer1 = request.POST.get("question1")
    # 关注人数比较多的中介/累计评价比较多的中介
    answer2 = request.POST.get("question2")
    # 近30天内带看房次数比较多的中介/神准时、活地图等标签在评论中占比比较高的中介
    answer3 = request.POST.get("question3")
    # 要被推荐的中介个数
    answer4 = request.POST.get("question4")

    # 根据用户的输入来调整权重矩阵
    if answer1 == "sale":
        w[3] = 0.1
        w[4] = 0
    elif answer1 == "rent":
        w[4] = 0.1
        w[3] = 0
    else:
        w[3], w[4] = 0.05, 0.05

    if answer2 == "follower":
        w[6] = 0.1
        w[2] = 0
    elif answer2 == "serviceyear":
        w[2] = 0.1
        w[6] = 0
    else:
        w[2], w[6] = 0.05, 0.05

    if answer3 == "30days":
        w[5] = 0.1
        w[7] = 0
    elif answer3 == "biaoqian":
        w[7] = 0.1
        w[5] = 0
    else:
        w[5], w[7] = 0.05, 0.05

    print("根据您的选择，权重矩阵调整后为：%s，推荐的中介个数为：%s" % (w,answer4))
    recommend_number = int(answer4)
    recommend_second = "Agent_Recommend_Git/data/result/recommend_yiju/recommend_second.csv"

    engine = get_engine(database_name)
    print("-------------- 开始进行后台处理 ----------------")
    # print("1.对分词结果进行分类",end=" ,")
    # seg_result_emotionwords(fenci_result, fenci_result_fenlei)
    # print("分类结果保存至 %s ." % fenci_result_fenlei)

    # print("2.计算评论情感得分并融合评分、服务年限、标签等按照权重 %s 得到最终推荐得分" % str(w),end=" ,")
    # get_emotion_score(fenci_result_fenlei, recommend_score, w)
    # print("推荐总得分已写入文件 %s ." % recommend_score)
    # print("    将融合后的推荐总得分recommend_score导入数据库 %s 的 %s 表中" % (database_name, zhongjian_recommend_score_table))
    # csv_to_database(engine, recommend_score, database_name, zhongjian_recommend_score_table)
    # print("    按照推荐总得分排序形成首要推荐依据",end=" ,")
    # recom_first(recommend_score, recommend_first)
    # print("    首要推荐依据已写入文件 %s ." % recommend_first)
    #
    # print("3.融合中介-词语矩阵和推荐总得分形成中介-情感矩阵，并计算相似度得到每个中介的邻居集，形成次要推荐依据",end=" ,")
    # final_df = ronghe_juzhen()
    # agent_list, similar_df = get_similar(final_df)
    # neighbors_result = get_k_neighbors(agent_list, similar_df, neighbors)
    # neighbors_result.to_csv(recommend_second, index=False)
    # print("所有中介的 %d 个邻居(即次要推荐依据)已写入文件 %s ." % (neighbors,recommend_second))

    print("4.根据首要推荐依据和次要推荐依据进行 %d 个中介的推荐" % recommend_number)
    recommend_list = get_first_recom(recommend_first)
    print("4.1 获取到的首要推荐依据为：%s" % recommend_list)
    recommend_second = get_second_recom(recommend_second)
    print("4.2 获取到的次要推荐依据(邻居集)为：%s" % recommend_second)
    final_result = recommend(recommend_list, recommend_second, recommend_number)

    # 根据final_result的推荐中介的列表去数据库里拿到其信息
    agent_infos = []
    for agent in final_result:
        agent_info = Agents_other_info.objects.get(agent_id=agent)
        agent_infos.append(agent_info)

    return render(request, 'recommend_result.html',{"quanzhong":w,"agent_num":answer4,"recommend_list":agent_infos})


def recommend_result(request):
    return render(request, 'recommend_result.html')
