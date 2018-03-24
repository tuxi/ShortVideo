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

from account.utils import get_token_data, create_login_token
from account.validators import validate_email, validate_password

@decorator_from_middleware(JwtAuthentication)
def get_user_data(request):
    token = get_token_data(request)
    username = token['username']

    try:
        u = UserProfile.objects.get(username=username).values('username', 'email')
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'data': {
                'message': 'The username does not exist'
            }
        }, status=500)

    return JsonResponse({
        'status': 'success',
        'data': u
    })

@decorator_from_middleware(JwtAuthentication)
def update_data(request):
    # only the email can be updated here
    token = get_token_data(request)
    username = token['username']

    post_data = json.loads(request.body.decode('utf-8'))
    new_email = post_data['email']

    try:
        validate_email(new_email)
    except ValidationError as e:
        return JsonResponse({
            'status': 'fail',
            'data': {
                'message': str(e)
            }
        }, status=500)

    # get user object
    u = UserProfile.objects.get(username=username)
    u.email = new_email
    try:
        u.save()
    except:
        return JsonResponse({
            'status': 'fail',
            'data': {
                'message': 'There was an error while updating user data'
            }
        }, status=500)

    token = create_login_token({'username': u.username, 'email': u.email})
    res = JsonResponse({
        'status': 'success'
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
            'data': {
                'message': str(e)
            }
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
                'data': {
                    'message': 'There was an error while updating the password'
                }
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
            'data': {
                'message': 'There was an error while deleting user account'
            }
        }, status=500)

    # need to delete jwt cookie on client side
    return JsonResponse({
        'status': 'success'
    })