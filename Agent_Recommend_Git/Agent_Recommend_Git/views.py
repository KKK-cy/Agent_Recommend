from django.http import HttpResponse
from django.shortcuts import render
from .other_scripts.get_recommend_score import GetRecommendScore
from .other_scripts.recommend_way import RecommendWay
from .other_scripts.get_emotion_juzhen import GetEmotionJuzhen
from .common import Common
from .database_settings import DatabaseSettings
from recommend_app.models import Agents_other_info
import warnings
warnings.filterwarnings("ignore")


"""
    下步优化处理：
    是否需要注册和登录界面？
    首页是否需要分页显示中介信息？
"""

# 系统主页，显示24名中介的名片卡信息
def home(request):
    agent_infos = Agents_other_info.objects.all()[:24]
    return render(request, 'home.html', {'agent_infos': agent_infos})


# 调查问卷页面
def showwenjuan(request):
    return render(request, 'wenjuan.html')


# 调查问卷提交的数据 --> 转变为权重参数
def wenjuan(request):
    settings = Common()
    database = DatabaseSettings()
    engine = database.get_engine()

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
        settings.w[3] = 0.1
        settings.w[4] = 0
    elif answer1 == "rent":
        settings.w[4] = 0.1
        settings.w[3] = 0
    else:
        settings.w[3], settings.w[4] = 0.05, 0.05

    if answer2 == "follower":
        settings.w[6] = 0.1
        settings.w[2] = 0
    elif answer2 == "serviceyear":
        settings.w[2] = 0.1
        settings.w[6] = 0
    else:
        settings.w[2], settings.w[6] = 0.05, 0.05

    if answer3 == "30days":
        settings.w[5] = 0.1
        settings.w[7] = 0
    elif answer3 == "biaoqian":
        settings.w[7] = 0.1
        settings.w[5] = 0
    else:
        settings.w[5], settings.w[7] = 0.05, 0.05

    print("根据您的选择，权重矩阵调整后为：%s，推荐的中介个数为：%s" % (settings.w, answer4))
    print("""即：
    中介原始评分均值对应权重<{w0}>，评论文本情感得分均值对应权重<{w1}>,
    服务年限对应权重<{w2}>，买卖房屋数量对应权重<{w3}>，
    租赁房屋数量对应权重<{w4}>，30天内带看房次数对应权重<{w5}>，
    关注人数对应权重<{w6}>，标签平均占比对应权重<{w7}>
    """.format(w0=settings.w[0], w1=settings.w[1], w2=settings.w[2], w3=settings.w[3], w4=settings.w[4],
               w5=settings.w[5], w6=settings.w[6], w7=settings.w[7]))

    recommend_number = int(answer4)

    print("----------------------- 1.评分扩展得到推荐总得分 ---------------------------")
    # print("1.根据权重{w}计算推荐总得分".format(w=settings.w))
    get_recommend_score_tender = GetRecommendScore(settings,database)
    # 从数据库中获取到预处理阶段的最终结果表df
    final_result_df = database.get_agent_info(engine,database.final_result_table)
    recommend_score_df = get_recommend_score_tender.get_recommend_score(final_result_df,settings.w)
    database.save_to_database(recommend_score_df,engine,database.recommend_score)
    print("推荐总得分的计算结果已插入<{table_name}>表".format(table_name=database.recommend_score))
    get_recommend_score_tender.recom_first(recommend_score_df,settings.recommend_first)
    print("首要推荐依据已保存至<{recommend_first}>".format(recommend_first=settings.recommend_first))
    # 首要推荐依据没有必要存至数据库中

    print("----------------------- 2.产生中介-情感矩阵 ---------------------------")
    emotion_juzhen_tender = GetEmotionJuzhen(settings, database)
    # 从数据库中获取到分词结果df，便于从中产生中介-词语矩阵
    fenci_result_df = database.get_agent_info(engine,database.fenci_result_table)
    final_df = emotion_juzhen_tender.ronghe_juzhen(fenci_result_df,recommend_score_df)

    print("----------------------- 3.计算相似度并保留邻居集 ---------------------------")
    print("根据中介-情感矩阵计算两两中介之间的相似度")
    agent_list, similar_df = emotion_juzhen_tender.get_similar(final_df)
    print("根据相似度的大小为每个中介保留{num}个邻居".format(num=settings.neighbors))
    neighbors_result = emotion_juzhen_tender.get_k_neighbors(agent_list, similar_df, settings.neighbors)
    neighbors_result.to_csv(settings.recommend_second, index=False)
    print(
        "邻居集(即次要推荐依据)已写入文件< {recommend_second} >，即将写入数据库".format(recommend_second=settings.recommend_second))
    database.csv_to_database(engine, settings.recommend_second, database.database_name, database.recommend_second_table)


    recommend_tender = RecommendWay(settings, database)
    print("----------------------- 4.产生{num}个中介的推荐列表 ---------------------------".format(num=recommend_number))
    recommend_list = recommend_tender.get_first_recom(settings.recommend_first)
    # print("4.1 获取到的首要推荐依据为：%s" % recommend_list)
    recommend_second = recommend_tender.get_second_recom(settings.recommend_second)
    # print("4.2 获取到的次要推荐依据(邻居集)为：%s" % recommend_second)
    final_result = recommend_tender.recommend(recommend_list, recommend_second, recommend_number)

    # 根据产生的推荐列表去数据库拿到其信息
    print("----------------------- 5.后台展示推荐列表 ---------------------------")
    agent_infos = []
    for agent in final_result:
        agent_info = Agents_other_info.objects.get(agent_id=agent)
        agent_infos.append(agent_info)

    # 在控制台输出一下推荐的中介信息，便于在论文第4章截图
    for recommend_agent in agent_infos:
        print("中介ID为：{agent_id}，姓名为{agent_name}".format(agent_id=recommend_agent.agent_id,
                                                        agent_name=recommend_agent.agent_name))
        print("个人主页为：{agent_url}".format(agent_url=recommend_agent.agent_url))
        print("服务年限为：{service_year}，买卖成交量为：{sale_number}，租赁成交量为{rent_number}".format(
            service_year=recommend_agent.service_year,
            sale_number=recommend_agent.sale_number,
            rent_number=recommend_agent.rent_number))
        print("30天内带看房次数为：{kanfang_number_30_days}，关注人数为{followers_number}".format(
            kanfang_number_30_days=recommend_agent.kanfang_number_30_days,
            followers_number=recommend_agent.followers_number
        ))
        print("-------------------------------------------------------")

    # 传入推荐中介信息，动态加载推荐结果页面
    return render(request, 'recommend_result.html',
                  {"quanzhong": settings.w, "agent_num": answer4, "recommend_list": agent_infos})


# 推荐结果展示页面
def recommend_result(request):
    return render(request, 'recommend_result.html')
