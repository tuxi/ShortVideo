# -*- coding: utf-8 -*-
# @Time    : 3/18/18 8:05 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url
from django.conf.urls import include
from . import views

test = [

    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.test_upload, name = 'upload'),
    url(r'^register/$', views.test_register, name = 'test_register'),
    url(r'^login/$', views.test_login, name = 'test_login'),
    url(r'^video/(?P<video_id>[a-zA-Z0-9]+)/$', views.videoDetail, name='videoDetail'),
]

videos_routes = [
    # 根据ids获取一组视频,ids 为字符串,每个id之间以逗号分割
    url(r'^getVideoByIds$', views.video_summary, name='videoSummary'),
    # 通过视频的id获取该视频的详细信息, video/1/
    url(r'^video/new$', views.new_video, name='new_video'),
    url(r'^video/(?P<video_id>[a-zA-Z0-9]+)/$', views.video_detail, name='videoDetails'),
    url(r'^video/(?P<video_id>[a-zA-Z0-9]+)/rating/$', views.getRating, name='getMovieRating'),
    url(r'^video/(?P<video_id>[0-9]+)/comments/$', views.get_comments, name='getMovieComments'),
]

rate_routes = [
    url(r'^rate$', views.rate, name='rate'),
]

comment_routes = [
    url(r'^comment$', views.comment, name='comment'),
    url(r'^comment/(?P<id>[0-9]+)/$', views.update_comment, name='update comment'),
]

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
    url(r'^user/delete/$', views.delete_account, name='delete user account')
]

urlpatterns = videos_routes + rate_routes + auth_routes + user_data_routes + comment_routes + test