from django.http import HttpResponse
from django.shortcuts import render
from recommend_app.models import Agents_other_info

""" 
主页：显示部分中介的名片卡 
"""
def home(request):
    agent_infos = Agents_other_info.objects.all()[:24]
    return render(request,'home.html',{'agent_infos':agent_infos})

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

    print(answer1)
    print(answer2)
    print(answer3)
    print(answer4)

    return render(request,'recommend_result.html')

def recommend_result(request):
    return render(request,'recommend_result.html')
