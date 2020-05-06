from django.shortcuts import render
from recommend_app.models import Agents_other_info

""" 
主页：显示部分中介的名片卡 
https://bj.5i5j.com/jingjiren/558757.html
"""
def home(request):
    agent_infos = Agents_other_info.objects.all()[:24]
    return render(request,'home.html',{'agent_infos':agent_infos})