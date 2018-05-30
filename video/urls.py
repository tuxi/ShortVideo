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
    # 获取全部视频
    url(r'^video/getAll$', views.getAll, name='getAll'),
    url(r'^video/getVideosByPage$', views.getVideosByPage, name='getVideosByPage'),
    # 根据用户id获取他所有的视频'
    url(r'^video/getVideoByUserId$', views.getVideoByUserId, name='getVideoByUserId'),
    # 根据ids获取一组视频,ids 为字符串,每个id之间以逗号分割
    url(r'^video/getVideoByIds$', views.getVideoByIds, name='getVideoByIds'),
    # 通过视频的id获取该视频的详细信息, video/1/
    url(r'^video/new$', views.new_video, name='new_video'),
    # 获取一个视频的详细信息 (注意: 参数中需要有user_id字段,获取某个用户的某个视频)
    url(r'^video/detail/$', views.video_detail, name='videoDetails'),
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


urlpatterns = videos_routes + rate_routes + comment_routes + test