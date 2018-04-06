# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:25 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : auth.py
# @Software: PyCharm


from django.http import JsonResponse
from account.models import UserProfile
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.core.exceptions import ValidationError
import json

from account.utils import create_login_token
from account.validators import validate_password, validate_email

def send_csrf(request):
    # just by doing this it will send csrf token back as Set-Cookie header
    csrf_token = get_token(request)
    return JsonResponse({
        'status': 'success',
        'csrftoken': csrf_token
    })

def username_exists(request):
    username = request.GET.get('u', '')

    try:
        u = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'status': 'success',
            'data': {
                'username_exists': False
            }
        })
    return JsonResponse({
        'status': 'success',
        'data': {
            'username_exists': True
        }
    })

def register(request):
    if request.method != 'POST':
        return JsonResponse({
            "status": "fail",
            "message": "必须是POST"
        })
        pass

    try:
        # 先通過json取值,如果數據不是json的就取POST參數中的
        post_data = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        post_data = request.POST
    username = post_data['username']
    try:
        # 先查找用戶名是否存在
        u = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        # 用戶名不存在,可以注冊
        nickname = post_data['nickname']
        email = post_data['email']
        password = post_data['password']
        confirm_password = post_data['confirm_password']
        gender = None
        if 'gender' in post_data:
            gender = post_data['gender']
        phone = None
        if 'phone' in post_data:
            phone = post_data['phone']
        birday = None
        if 'birday' in post_data:
            birday = post_data['birday']
        address = None
        if 'address' in post_data:
            address = post_data['address']

        avatar = None
        if 'avatar' in request.FILES:
            avatar = request.FILES.get('avatar', None)
        if password != confirm_password:
            return JsonResponse({
                'status': 'fail',
                'message': '兩次密碼不一致'
            }, status=500)
        try:
            validate_password(password)
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({
                'status': 'fail',
                'message': str(e)
            }, status=500)

        # 注冊用戶
        try:
            u = UserProfile.objects.create_user(
                username=username, nickname=nickname,
                password=password, email=email,
                gender=gender, phone=phone,
                birday=birday, avatar=avatar,
                address=address
            )
            u.save()
        except:
            return JsonResponse({
                'status': 'fail',
                'message': 'There was an error during registration'
            }, status=500)

        # 跳轉向到登錄界面
        return login(request=request, redirect_after_registration=True, redirect_user=u, registration_data={'username': username, 'email': email})

    # 用戶名已存在,無法完成注冊, 並告訴客戶端
    return JsonResponse({
        'status': 'fail',
        'message': 'username exists',
    })



def login(request, redirect_after_registration=False, redirect_user=None, registration_data=None):
    '''登錄完成後返回token,並將token放在cookie中'''

    user_dic = {}
    if redirect_after_registration:
        token = create_login_token(registration_data)
        if len(token):
            if redirect_user:
                user_dic = redirect_user.to_dict()
    else:
        try:
            post_data = json.loads(request.body.decode('utf-8'))
            username = post_data['username']
            password = post_data['password']
        except Exception as e:
            if request.method == 'POST':
                username = request.POST['username']
                password = request.POST['password']
            else:
                username = request.GET['username']
                password = request.GET['password']
        u = authenticate(username=username, password=password)
        # 如果用戶已被認證,則根據用戶名和用戶郵箱創建token,並返回客戶端
        if u is not None:
            token = create_login_token({'username': u.username, 'email': u.email})
        else:
            return JsonResponse({
                'status': 'fail',
                'message': '賬號或密碼錯誤',
            }, status=401)

        user_dic = u.to_dict()
    print('token is', token['token'])

    res = JsonResponse({
        'status': 'success',
        'user': user_dic,
        'token': str(token['token'], 'utf-8')
    })
    res.set_cookie('token', value=token['token'], expires=token['exp'])
    return res
