# -*- coding: utf-8 -*-
# @Time    : 3/23/18 11:56 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url
from . import views

auth_routes = [
    url(r'^auth/csrf$', views.send_csrf, name='send csrf token'),
    url(r'^auth/login/$', views.login, name='login'),
    url(r'^auth/register/$', views.register, name='register'),
    url(r'^auth/username-exists/$', views.username_exists, name='check unique username'),
]

user_data_routes = [
    url(r'^user/get-data/$', views.get_user_data, name='get user data'),
    url(r'^user/update/$', views.update_data, name='update user data'),
    url(r'^user/update-password/$', views.update_password, name='update user password'),
    url(r'^user/delete/$', views.delete_account, name='delete user account'),

]

urlpatterns = auth_routes + user_data_routes