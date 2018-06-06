# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:31 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : account.py
# @Software: PyCharm

from django.utils.decorators import decorator_from_middleware
from account.middlewares.jwt_authentication import JwtAuthentication
from account.models import UserProfile
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import json
from video.models import VideoItem, Likes

from account.utils import get_token_data, create_login_token
from account.validators import validate_email, validate_password
from dss.Serializer import serializer

@decorator_from_middleware(JwtAuthentication)
def get_user_data(request):
    token = get_token_data(request)
    username = token['username']

    try:
        u = UserProfile.objects.get(username=username).values('username', 'email')
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': 'The username does not exist'
        }, status=500)

    return JsonResponse({
        'status': 'success',
        'data': u
    })

@decorator_from_middleware(JwtAuthentication)
def update_data(request):
    '''
    更新用户信息, 根据用户登录时的token进行更新
    :param request:
    :return:
    '''
    if request.method != 'POST':
        return JsonResponse({
            'status': 'fail',
            'message': '本接口只支持post'
        })
    token = get_token_data(request)
    username = token['username']
    u = UserProfile.objects.get(username=username)
    if username is None or len(username) == 0 or u is None:
        return JsonResponse({
            'status': 'fail',
            'message': '没有权限,用户未登录'
        })

    new_email = request.POST.get('email')
    new_nickname = request.POST.get('nickname')
    new_gender = request.POST.get('gender')
    new_birday = request.POST.get('birday')
    new_address = request.POST.get('address')
    new_summary = request.POST.get('summary')
    new_avatar = u.avatar
    new_cover = u.cover
    if 'avatar' in request.FILES:
        new_avatar = request.FILES.get('avatar', None)
    if 'cover' in request.FILES:
        new_cover = request.FILES.get('cover', None)

    try:
        if new_email is not None:
            validate_email(new_email)
    except ValidationError as e:
        return JsonResponse({
            'status': 'fail',
            'message': str(e)
        }, status=500)

    if new_email is not None:
        # email is not none
        u.email = new_email
    u.nickname = new_nickname
    u.gender = new_gender
    u.address = new_address
    u.cover = new_cover
    u.avatar = new_avatar
    u.birday = new_birday
    u.summary = new_summary
    try:
        u.save()
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': str(e)
        }, status=500)

    token = create_login_token({'username': u.username, 'email': u.email})
    res = JsonResponse({
        'status': 'success',
        'user': u.to_dict(),
    })
    res.set_cookie('token', value=token['token'], expires=token['exp'])
    return res

def update_password(request):
    token = get_token_data(request)
    username = token['username']

    post_data = json.loads(request.body.decode('utf-8'))
    new_password = post_data['password']
    old_password = post_data['oldPassword']

    try:
        validate_password(new_password)
    except ValidationError as e:
        return JsonResponse({
            'status': 'fail',
            'message': str(e)
        }, status=500)

    # check old password and get user object
    u = authenticate(username=username, password=old_password)
    if u is not None:
        u.set_password(new_password)
        try:
            u.save()
        except:
            return JsonResponse({
                'status': 'fail',
                'message': 'There was an error while updating the password'
            }, status=500)

        return JsonResponse({
            'status': 'success'
        })
    else:
        return JsonResponse({
            'status': 'fail'
        }, status=401)

def delete_account(request):
    if request.method != 'DELETE':
        pass

    token = get_token_data(request)
    username = token['username']

    u = UserProfile.objects.get(username=username)
    try:
        u.delete()
    except:
        return JsonResponse({
            'status': 'fail',
            'message': 'There was an error while deleting user account'
        }, status=500)

    # need to delete jwt cookie on client side
    return JsonResponse({
        'status': 'success'
    })

#@decorator_from_middleware(JwtAuthentication)
def search(request):
    if request.method == 'POST':
        return JsonResponse({
            'status': 'fail',
            'message': '必须是GET请求',
        })

    try:
        username = request.GET.get('username')
        # auth_username = request.GET.get('auth_username')
        if username is None or len(username) == 0:
            return JsonResponse({
                'status': 'fail',
                'message': '未知搜索對象:username不能爲空'
            })
        # 搜索类型, 暂定1 为搜索用户个人主页所有信息
        type = int(request.GET.get('type'))
        if type is not 1:
            return JsonResponse({
                'status': 'fail',
                'message': '未知搜索type, type不能爲空'
            })
        # if auth_username != None:
        #     # 如果授权用户不存在,则抛出异常
        #     auth_user = UserProfile.objects.filter(username=auth_username).first()
        #     token = get_token_data(request)
        #     token_username = token['username']
        #     # 如果授權的用戶信息與參數中auth_username不一致,則拋出異常
        #     if auth_user.username != token_username:
        #         return JsonResponse({
        #             'status': 'fail',
        #             'message': '用戶授權信息錯誤'
        #         })
        search_user = UserProfile.objects.filter(username=username).first()
        search_dict = search_user.to_dict()
        # 獲取用戶發布的所有視頻
        my_videos = VideoItem.objects.filter(user__username=username)
        if my_videos is None:
            my_videos = []

        my_videos = VideoItem.to_dict_list(my_videos)
        search_dict['my_videos'] = my_videos
        # 獲取用戶點贊的所有視頻
        my_likes = Likes.objects.filter(user__username=username)
        if my_likes is None:
            my_likes = []
        my_likes = serializer(data=my_likes)
        search_dict['my_likes'] = my_likes
        return JsonResponse({
            'status': 'success',
            'data': search_dict
        })
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': str(e)
        }, status=500)

