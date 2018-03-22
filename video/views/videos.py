# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:16 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : videos.py
# @Software: PyCharm
import json

from django.http import JsonResponse
from django.db.models import Avg, Count, Func

from video.utils import get_token_data
from ..models import VideoItem, Rating, Comment
from video.middlewares.jwt_authentication import JwtAuthentication
from django.utils.decorators import decorator_from_middleware
from django.contrib.auth.models import User
from django.core import serializers

@decorator_from_middleware(JwtAuthentication)
def new_video(request):
    # 上传文件必须是post请求
    if request.method != 'POST':
        pass

    token = get_token_data(request)
    username = token['username']

    try:
        u = User.objects.get(username=username)#.values('username', 'email')
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'data': {
                'message': 'The username does not exist'
            }
        }, status=500)

    user_id = u.pk
    # 用户必须登录
    if user_id == None:
        pass

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
                'data': {
                    'message': str(e) if type(e) == ValueError else 'Error while saving movie'
                }
            }, status=500)

        return JsonResponse({
            'status': 'success',
            'data': {
                'title': m.title
            }
        })
    return JsonResponse({
        'status': 'fail',
        'data': {
            'message': ""
        }
    })


def video_detail(request):
    if request.method != 'GET':
        pass

    # 获取视频
    try:
        data = json.loads(request.body.decode('utf-8'))
        video_id = data['data']
    except Exception as e:
        video_id = request.GET['user_id']
    try:
        m = VideoItem.objects.get(pk=video_id)
    except VideoItem.DoesNotExist:
        return JsonResponse({
            'status': 'success',
            'data': {
                'rating': {
                    'avg': None,
                    'comments': None
                }
            }
        })

    # get rating
    r = Rating.objects.filter(video=m)\
        .values('rating')\
        .aggregate(
            avg_rating=Avg('rating'),
            rating_count=Count('rating')
        )
    avg_rating = r['avg_rating']
    rating_count = r['rating_count']

    # get comments
    c = Comment.objects.filter(video=m).values('body', 'username')

    return JsonResponse({
        'status': 'success',
        'data': {
            'rating': {
                'avg': '{:.1f}'.format(avg_rating) if avg_rating is not None else None,
                'count': rating_count
            },
            'comments': list(c)
        }
    })

class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 1)'

def getVideoByUserId(request):
    '''根据用户id获取他所有的视频'''
    if request.method != 'GET':
        pass

    # 获取所有请求的视频id
    user_id = request.GET.get('user_id', '')

    video_list = VideoItem.objects.filter(user_id=user_id).annotate(
        avg_rating=Round(Avg('rating__rating')), # avg on rating column of rating table
        comment_count=Count('comment', distinct=True)
    ).values()

    video_list = serializers.serialize('json', video_list)

    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': video_list
        }
    })

def getVideoByIds(request):
    '''根据一组id获取对应的一组视频'''
    if request.method != 'GET':
        pass

    # 获取所有请求的视频id
    video_ids = request.GET.get('ids', '').split(',')

    video_list = VideoItem.objects.filter(id__in=video_ids).annotate(
        avg_rating=Round(Avg('rating__rating')), # avg on rating column of rating table
        comment_count=Count('comment', distinct=True)
    ).values()

    video_lsit = serializers.serialize('json', video_list)
    if video_list == None:
        video_list = []

    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': video_lsit
        }
    })
def getAll(request):
    '''根据一组id获取对应的一组视频'''
    if request.method != 'GET':
        pass

    video_list = VideoItem.objects.all()
    video_list = serializers.serialize('json', video_list)
    if video_list == None:
        video_list = []
    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': video_list
        }
    })
