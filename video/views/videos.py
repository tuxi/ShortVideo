# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:16 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : videos.py
# @Software: PyCharm

from django.http import JsonResponse
from django.db.models import Avg, Count, Func
from ..models import VideoItem, Rating, Comment


def new_video(request):
    if request.method != 'POST':
        pass

    # 获取视频数据
    id = request.POST.get('id', '')
    title = request.POST.get('title', '')
    describe = request.POST.get('describe', '')
    # save new movie
    m = VideoItem(source_id = id, title = title, describe = describe)
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


def video_detail(request, video_id):
    if request.method != 'GET':
        pass

    # get movie
    try:
        m = VideoItem.objects.get(source_id=video_id)
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

def video_summary(request):
    if request.method != 'GET':
        pass

    # 获取所有请求的视频id
    video_ids = request.GET.get('ids', '').split(',')

    m = VideoItem.objects.filter(source_id__in=video_ids).annotate(
        avg_rating=Round(Avg('rating__rating')), # avg on rating column of rating table
        comment_count=Count('comment', distinct=True)
    ).values()

    videos = {}
    for video in list(m):
        videos[video.get('source_id')] = video

    return JsonResponse({
        'status': 'success',
        'data': {
            'videos': videos
        }
    })
