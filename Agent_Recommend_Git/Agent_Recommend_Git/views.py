from django.shortcuts import render
from recommend_app.models import Agents_other_info

""" 主页：显示部分中介的名片卡 """
def home(request):
    return render(request,'home.html')