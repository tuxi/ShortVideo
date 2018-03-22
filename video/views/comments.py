# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:27 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : comments.py
# @Software: PyCharm

from django.http import JsonResponse
import math
import json

from ..models import Comment, VideoItem
from video.utils import get_token_data

# @csrf_exempt # temporary decorator to remove csrf, just to test with postman
def comment(request):
    if request.method == 'POST':
        post_data = json.loads(request.body.decode('utf-8'))
        video_id = post_data['id']
        body = post_data['body']

        try:
            username = post_data['username']
        except KeyError:
            token = get_token_data(request)
            username = token['username']

        # 获取视频模型对象
        m, created = VideoItem.objects.get_or_create(pk = video_id, defaults={'title': ''})
        # comment
        c = Comment(video = m, username = username, body = body)
        try:
            c.save()
        except:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': 'Error while saving comment'
                }
            }, status=500)

        return JsonResponse({
            'status': 'success',
            'data': {
                'id': c.id
            }
        })
    elif request.method == 'DELETE':
        id = request.GET.get('id', '')
        username = request.GET.get('u', '')

        try:
            c = Comment.objects.get(id=id, username=username)
        except Comment.DoesNotExist:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': 'This comment does not exist'
                }
            }, status=500)

        try:
            c.delete()
        except:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': 'Error while deleting comment'
                }
            }, status=500)

        return JsonResponse({
            'status': 'success'
        })

def get_comments(request, vid):
    if request.method != 'GET':
        pass

    items_per_page = 7
    page = int(request.GET.get('p', 1))

    c = Comment.objects.filter(video_id=vid).order_by('-date')
    total_pages = math.ceil(c.count() / items_per_page)

    page = page-1 if page <=total_pages or total_pages==0 else total_pages-1
    limits = {
        'from': items_per_page * page,
        'to': (items_per_page * page) + items_per_page
    }

    comments = c[limits['from']: limits['to']].values()

    return JsonResponse({
        'status': 'success',
        'data': {
            'comments': list(comments),
            'total_pages': total_pages,
            'current_page': page+1,
            'items_per_page': items_per_page
        }
    })

# not currently used
def update_comment(request, id):
    if request.method != 'POST':
        pass

    username = request.POST.get('username', '')
    body = request.POST.get('body', '')

    try:
        c = Comment.objects.get(id=id, username=username)
    except Comment.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'data': {
                'message': 'This comment does not exist'
            }
        }, status=500)

    c.body = body
    try:
        c.save()
    except:
        return JsonResponse({
            'status': 'fail',
            'data': {
                'message': 'Error while updating comment'
            }
        })

    return JsonResponse({
        'status': 'success'
    })