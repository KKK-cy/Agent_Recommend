"""Agent_Recommend_Git URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path

from Agent_Recommend_Git import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 登录
    url(r'^login/', views.login),
    # 注册
    url(r'^register/', views.register),
    # 登出
    url(r'^logout/', views.logout),

    # 系统首页
    path('', views.login),
    url(r'^home.html', views.home),
    re_path('wenjuan/$', views.showwenjuan),
    re_path('recommend_result$', views.wenjuan),
    # 情感分析相关页面
    re_path('emotion/$', views.showemotion),
    re_path('hotwords/$', views.showhotwords),
    re_path('visual/$', views.showvisual)
]
