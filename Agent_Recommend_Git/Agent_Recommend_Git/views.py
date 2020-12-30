from django.http import HttpResponse
from django.shortcuts import render
from Agent_Recommend_Git.other_scripts.datasets_pretreatment_1 import comment_chuli, other_chuli, pre_result_to_database
from Agent_Recommend_Git.other_scripts.get_degree_words_2 import fenci
from Agent_Recommend_Git.other_scripts.agent_emotion_juzhen_5 import ronghe_juzhen, get_similar, get_k_neighbors
from Agent_Recommend_Git.other_scripts.fenci_result_fenlei_3 import seg_result_emotionwords
from Agent_Recommend_Git.other_scripts.get_recommend_score_4 import get_emotion_score, recom_first
from Agent_Recommend_Git.other_scripts.recommend_way_6 import get_first_recom, get_second_recom, recommend
from recommend_app.models import Agents_other_info
from Agent_Recommend_Git.seetings import w, fenci_result, fenci_result_fenlei, recommend_score, csv_to_database, \
    database_name, zhongjian_recommend_score_table, recommend_first, recommend_second, get_engine, neighbors, \
    agent_comments, chuli_agent_comments, agent_other_information, chuli_agent_other_information

import warnings

warnings.filterwarnings("ignore")


# 系统主页，显示24名中介的名片卡信息
def home(request):
    agent_infos = Agents_other_info.objects.all()[:24]
    return render(request, 'home.html', {'agent_infos': agent_infos})


# 调查问卷页面
def showwenjuan(request):
    return render(request, 'wenjuan.html')


# 调查问卷提交的数据 --> 转变为权重参数
def wenjuan(request):
    # 获取买卖房屋还是租赁房屋
    answer1 = request.POST.get("question1")
    # 关注人数比较多的中介/累计评价比较多的中介
    answer2 = request.POST.get("question2")
    # 近30天内带看房次数比较多的中介/神准时、活地图等标签在评论中占比比较高的中介
    answer3 = request.POST.get("question3")
    # 要被推荐的中介个数
    answer4 = request.POST.get("question4")

    # 根据用户的选择来调整权重矩阵
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

    print("根据您的选择，权重矩阵调整后为：%s，推荐的中介个数为：%s" % (w, answer4))
    recommend_number = int(answer4)
    recommend_second = "Agent_Recommend_Git/data/result/recommend_yiju/recommend_second.csv"

    engine = get_engine(database_name)

    """ 
        一些基本的处理工作（不用重复执行）：
        1.对爬取到的评论文本进行预处理，另存为新文件并存入数据库
        2.对预处理后的评论文本进行分词
        3.对分词结果进行分类
    """
    # print(
    #     "1.对爬取到的中介评论文件< {agent_comments} >和中介其它信息文件< {agent_other_information} >进行预处理，结果分别存至< {chuli_agent_comments} >和< {chuli_agent_other_information} >".format(
    #         agent_comments=agent_comments, agent_other_information=agent_other_information,
    #         chuli_agent_comments=chuli_agent_comments, chuli_agent_other_information=chuli_agent_other_information))
    # comment_chuli(agent_comments, chuli_agent_comments)
    # other_chuli(agent_other_information, chuli_agent_other_information)
    # pre_result_to_database(engine)
    #
    # print("2.对预处理后的评论文件< {chuli_agent_comments} >进行分词，分词结果存至< {fenci_result} >".format(
    #     chuli_agent_comments=chuli_agent_comments,
    #     fenci_result=fenci_result))
    # fenci(chuli_agent_comments, fenci_result)
    #
    # print("3.对分词结果进行分类，分类结果存至< {fenci_result_fenlei} >".format(fenci_result_fenlei=fenci_result_fenlei))
    # seg_result_emotionwords(fenci_result, fenci_result_fenlei)

    print("1.按照权重{w}融合评论情感得分值和其它维度信息计算 推荐总得分".format(w=w))
    get_emotion_score(fenci_result_fenlei, recommend_score, w)
    print("推荐总得分已写入文件< {recommend_score} >，即将写入数据库".format(recommend_score=recommend_score))
    csv_to_database(engine, recommend_score, database_name, zhongjian_recommend_score_table)
    print("按照推荐总得分排序形成首要推荐依据并写入文件<{recommend_first}>".format(recommend_first=recommend_first))
    recom_first(recommend_score, recommend_first)

    print("2.融合中介-词语矩阵和推荐总得分形成中介-情感矩阵")
    final_df = ronghe_juzhen()
    print("根据中介-情感矩阵计算两两中介之间的相似度")
    agent_list, similar_df = get_similar(final_df)
    print("根据相似度的大小为每个中介保留{num}个邻居".format(num=neighbors))
    neighbors_result = get_k_neighbors(agent_list, similar_df, neighbors)
    neighbors_result.to_csv(recommend_second, index=False)
    print(
        "所有中介的{num}个邻居(即次要推荐依据)已写入文件< {recommend_second} > .".format(num=neighbors, recommend_second=recommend_second))

    print("6.根据首要推荐依据和次要推荐依据进行 %d 个中介的推荐" % recommend_number)
    recommend_list = get_first_recom(recommend_first)
    # print("4.1 获取到的首要推荐依据为：%s" % recommend_list)
    recommend_second = get_second_recom(recommend_second)
    # print("4.2 获取到的次要推荐依据(邻居集)为：%s" % recommend_second)
    final_result = recommend(recommend_list, recommend_second, recommend_number)

    # 根据产生的推荐列表去数据库拿到其信息
    agent_infos = []
    for agent in final_result:
        agent_info = Agents_other_info.objects.get(agent_id=agent)
        agent_infos.append(agent_info)
    # 传入推荐中介信息，动态加载推荐结果页面
    return render(request, 'recommend_result.html',
                  {"quanzhong": w, "agent_num": answer4, "recommend_list": agent_infos})


def recommend_result(request):
    return render(request, 'recommend_result.html')
