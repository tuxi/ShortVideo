# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:29 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : ratings.py
# @Software: PyCharm

from django.http import JsonResponse
import json

from account.utils import get_token_data
from ..models import Rating, VideoItem


def rate(request):

    # if POST, save or update rating
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        video_id = body['id']
        rating = int(body['rating'])

        try:
            username = body['username']
        except KeyError:
            token = get_token_data(request)
            username = token['username']

        # get the video object with id video_id, or create it
        m, created = VideoItem.objects.get_or_create(pk=video_id, defaults={'title': ''})
        # save or update rating
        try:
            r, created = Rating.objects.update_or_create(username=username, video=m, defaults={'rating': rating})
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': 'Error while saving rating'
                }
            }, status=500)

        return JsonResponse({
            'status': 'success',
            'data': {
                'title': m.title,
                'rating': r.rating,
                'is_new': created
            }
        })
    elif request.method == 'DELETE':
        username = request.GET.get('u', '')
        video_id = request.GET.get('m_id', '')

        # find movie object
        m = VideoItem.objects.filter(pk=video_id).first()
        r = Rating.objects.filter(video=m, username=username)

        # delete rating
        try:
            r.delete()
        except:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': 'Error while deleting rating'
                }
            }, status=500)

        return JsonResponse({
            'status': 'success'
        })

def getRating(request, video_id):
    if request.method != 'POST':
        pass

    body = json.loads(request.body.decode('utf-8'))
    username = body['username']

    # get rating
    r = Rating.objects.filter(video_id = video_id, username = username).first()

    return JsonResponse({
        'result': 'success',
        'data': {
            'rating': r.rating if r else None
        }
    })