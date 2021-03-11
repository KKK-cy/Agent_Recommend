from django.http import HttpResponse
from django.shortcuts import render, redirect

from .other_scripts.hotwords_visual import HotwordsVisual
from .other_scripts.get_recommend_score import GetRecommendScore
from .other_scripts.recommend_way import RecommendWay
from .other_scripts.get_emotion_juzhen import GetEmotionJuzhen
from .common import Common
from .database_settings import DatabaseSettings
from recommend_app.models import Agents_other_info, User,Agent_scores,Agent_emotion_juzhen
from .forms import UserForm, RegisterForm
import warnings
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")


def login(request):
    agent_infos = Agents_other_info.objects.all()[:24]
    if request.session.get('is_login', None):
        return render(request, "home.html",{'agent_infos': agent_infos})

    if request.method == "POST":
        # 获取登录界面传入的用户名和密码
        login_form = UserForm(request.POST)
        message = "请检查您输入的用户名和密码！"
        # 使用is_valid验证数据
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            try:
                user = User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect("/home.html",{'agent_infos': agent_infos})

                else:
                    message = "密码错误！"
            except:
                message = "该用户在系统中不存在！"
        return render(request, "login.html", locals())
    login_form = UserForm()
    return render(request, 'login.html', locals())


def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())

                # 当一切都OK的情况下，创建新用户
                new_user = User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("home.html")
    request.session.flush()
    return redirect('/login/')


# 系统主页，显示24名中介的名片卡信息
def home(request):
    agent_infos = Agents_other_info.objects.all()[:30]
    return render(request, 'home.html', {'agent_infos': agent_infos})


# 调查问卷页面
def showwenjuan(request):
    return render(request, 'wenjuan.html',)

# 情感分析结果展示页面
def showemotion(request):
    agent_score_infos = Agent_scores.objects.all()[:30]
    return render(request, 'emotion.html',{'agent_score_infos': agent_score_infos})

# 热词展示页面
def showhotwords(request):
    settings = Common()
    database = DatabaseSettings()
    engine = database.get_engine()

    hotwords_tender = HotwordsVisual(settings, database)
    fenci_result_fenlei_df = database.get_agent_info(engine, database.fenci_result_fenlei_table)
    # 热词词典{热词：出现次数}
    hotwords_dict = hotwords_tender.hotwords_ciyun(fenci_result_df=fenci_result_fenlei_df)
    print("1.热门词语的出现次数字典为：",hotwords_dict)
    # 根据所有词语的出现次数产生词云文件
    print("2.开始根据热门词语字典生成< 热词词云图 >")
    wc1 = WordCloud(font_path='/font/msyh.ttc', background_color='white').generate_from_frequencies(hotwords_dict)
    fig = plt.figure(num="中介评论情感分析与协同过滤推荐系统--热词词云")
    plt.imshow(wc1)
    plt.axis('off')
    plt.show()

    plt.savefig(settings.ciyun_file, dpi=500)
    print("3.生成的热词词云图已保存至本地{ciyun_file}".format(ciyun_file=settings.ciyun_file))

    # 后面考虑指定词云的形状

    return render(request, 'hotwords.html',{'img_file':settings.ciyun_file})

# 评论热词可视化展示页面
def showvisual(request):
    # 调用表agent_emotion_juzhen中的数据渲染页面
    agent_infos = Agent_emotion_juzhen.objects.all()[:30]
    return render(request, 'visual.html',{'agent_infos': agent_infos})

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
    get_recommend_score_tender = GetRecommendScore(settings, database)
    # 从数据库中获取到预处理阶段的最终结果表df
    final_result_df = database.get_agent_info(engine, database.final_result_table)
    recommend_score_df = get_recommend_score_tender.get_recommend_score(final_result_df, settings.w)
    database.save_to_database(recommend_score_df, engine, database.recommend_score)
    print("推荐总得分的计算结果已插入<{table_name}>表".format(table_name=database.recommend_score))
    get_recommend_score_tender.recom_first(recommend_score_df, settings.recommend_first)
    print("首要推荐依据已保存至<{recommend_first}>".format(recommend_first=settings.recommend_first))
    # 首要推荐依据没有必要存至数据库中

    print("----------------------- 2.产生中介-情感矩阵 ---------------------------")
    emotion_juzhen_tender = GetEmotionJuzhen(settings, database)
    # 从数据库中获取到分词结果df，便于从中产生中介-词语矩阵
    fenci_result_fenlei_df = database.get_agent_info(engine, database.fenci_result_fenlei_table)
    final_df = emotion_juzhen_tender.ronghe_juzhen(fenci_result_fenlei_df, recommend_score_df)

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
