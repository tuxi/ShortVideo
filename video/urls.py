# -*- coding: utf-8 -*-
# @Time    : 3/18/18 8:05 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url
from django.conf.urls import include
from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^upload/', views.upload, name = 'upload'),
]
