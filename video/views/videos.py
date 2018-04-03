# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:16 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : videos.py
# @Software: PyCharm
import json
from dss.Serializer import serializer
from django.http import JsonResponse
from django.db.models import Avg, Count, Func

from account.utils import get_token_data
from ..models import VideoItem, Rating, Comment
from account.middlewares.jwt_authentication import JwtAuthentication
from django.utils.decorators import decorator_from_middleware
from account.models import UserProfile
from django.core import serializers

@decorator_from_middleware(JwtAuthentication)
def new_video(request):
    # 上传文件必须是post请求
    if request.method != 'POST':
        return JsonResponse({
            'status': 'fail',
            'message': '上傳視頻必須使用POST',
        })

    token = get_token_data(request)
    username = token['username']

    try:
        u = UserProfile.objects.get(username=username)#.values('username', 'email')
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '用戶名不存在',
        }, status=500)

    user_id = u.pk
    # 用户必须登录
    if user_id == None:
        return JsonResponse({
            'status': 'fail',
            'message': '上傳視頻,用戶必須登錄'
        })

    # 获取视频数据
    title = request.POST.get('title', '')
    describe = request.POST.get('describe', '')
    # save
    video = request.FILES.get('video', None)

    if video:
        m = VideoItem(title = title, describe = describe, video = video, user_id = user_id)
        try:
            m.save()
            m.video_mp4.generate()
            m.video_ogg.generate()
        except Exception as e:
            return JsonResponse({
                'status': 'fail',
                'message': str(e) if type(e) == ValueError else '保存視頻出錯'
            }, status=500)
        # 重新查詢一遍視頻,返回給客戶端
        return getVideoDetailByVideoId(m.pk)
    return JsonResponse({
        'status': 'fail',
        'message': "未知錯誤"
    })


def video_detail(request):
    if request.method != 'GET':
        return JsonResponse({
            'status': 'fail',
            'message': '必须使用GET方法请求',
        })

    # 获取视频
    try:
        data = json.loads(request.body.decode('utf-8'))
        video_id = data['video_id']
    except Exception as e:
        video_id = request.GET['video_id']
    return getVideoDetailByVideoId(video_id)


# 公共方法,根據視頻的id,查詢視頻詳情,並以json的形式返回
def getVideoDetailByVideoId(video_id):
    try:
        m = VideoItem.objects.get(pk=video_id)
    except VideoItem.DoesNotExist:
        return JsonResponse({
            'status': 'success',
            'message': '视频不存在'
        })

    # 对象转化为字典
    videoDict = m.to_dict()
    return JsonResponse({
        'status': 'success',
        'data': {
            'video': videoDict,
        }
    })

class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 1)'

def getVideoByUserId(request):
    '''根据用户id获取他所有的视频'''
    if request.method != 'GET':
        return JsonResponse({
            'status': 'fail',
            'message': '必须使用GET方法请求',
        })

    # 获取所有请求的视频id
    user_id = request.GET.get('user_id', '')

    video_list = VideoItem.objects.filter(user_id=user_id).annotate(
        avg_rating=Round(Avg('rating__rating')), # avg on rating column of rating table
        comment_count=Count('comment', distinct=True)
    )#.values()

    videos = VideoItem.to_dict_list(video_list)
    if videos == None:
        videos = []

    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': videos
        }
    })

def getVideoByIds(request):
    '''根据一组id获取对应的一组视频'''
    if request.method != 'GET':
        return JsonResponse({
            'status': 'fail',
            'message': '必须使用GET方法请求',
        })

    # 获取所有请求的视频id
    video_ids = request.GET.get('ids', '').split(',')

    video_list = VideoItem.objects.filter(id__in=video_ids).annotate(
        avg_rating=Round(Avg('rating__rating')), # avg on rating column of rating table
        comment_count=Count('comment', distinct=True)
    )#.values()

    videos = VideoItem.to_dict_list(video_list)
    if videos == None:
        videos = []

    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': videos
        }
    })
def getAll(request):
    '''获取全部视频'''
    if request.method != 'GET':
        return JsonResponse({
            'status': 'fail',
            'message': '必须使用GET方法请求',
        })

    # 序列化对象
    # video_list = serializers.serialize('json', video_list)
    video_list = VideoItem.objects.all()
    videos = VideoItem.to_dict_list(video_list)
    if videos == None:
        videos = []
    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': videos
        }
    })
