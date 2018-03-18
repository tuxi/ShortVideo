# -*- coding: utf-8 -*-
# @Time    : 3/18/18 8:05 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from django.urls import path
from django.conf.urls import include
from . import views


urlpatterns = [
    #此处设置为首页，以前写法是'^$',新版本不再使用^、$，只需要‘’就可以
    # path('',  views.IndexView.as_view(), name='index'),
]

app_name='video'