# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:56 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : test.py
# @Software: PyCharm
import json

from django.contrib.auth import authenticate
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from video.models import VideoItem, Category, Likes
from ShortVideo.settings import PAGINATE_BY
from video.forms import MediaItemUploadForm
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from video.utils import create_login_token
from video.validators import validate_password, validate_email
from django.contrib.auth.models import User

def index(request):
    template = 'video/video_index.html'

    media_items = VideoItem.objects.all()

    print(len(media_items))
    context = {
        'media_items' : media_items,
    }

    return render(request, template, context = context)


def test_upload(request):
    template = 'video/upload.html'
    upload_media_form = MediaItemUploadForm()
    if request.method == 'POST':
        upload_media_form = MediaItemUploadForm(request.POST, request.FILES)

        if upload_media_form.is_valid():
            video = request.FILES.get('video', None)

            if video:
                media_item = VideoItem(video = video)
                media_item.save()

                media_item.video_mp4.generate()
                media_item.video_ogg.generate()
                return HttpResponseRedirect(reverse('video:index'))

    context = {
        'upload_media_form' : upload_media_form,
    }

    return render(request, template, context)

def test_register(request):
    template = 'user/register.html'
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        sex = request.POST['sex']
        phone1 = request.POST['phone1']
        if password != confirm_password:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': '兩次密碼不一致'
                }
            }, status=500)
        try:
            validate_password(password)
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': str(e)
                }
            }, status=500)

        # register user
        try:
            u = User.objects.create_user(username=username, password=password, email=email)
            u.save()
        except Exception as e:
            error = str(e)
            if len(error) == 0:
                error = 'There was an error during registration'
            return JsonResponse({
                'status': 'fail',
                'data': {
                    'message': error
                }
            }, status=500)

        # login user
        return test_login(request, True, {'username': username, 'email': email})


    return render(request, template)

def test_login(request, redirect_after_registration=False, registration_data=None):
    template = 'user/login.html'

    return render(request, template)


def videoDetail(request, vid):
    '''视频详情页'''
    # 获取视频分类作为菜单数据
    menu_list = Category.objects.all()
    # 获取视频数据
    id = int(vid)
    video = VideoItem.objects.get(id=id)
    try:
        video.viewed()
    except Exception as e:
        print(e)

    # 获取点赞数
    try:
        likes = Likes.objects.filter(video=video).count()
    except Exception as e:
        likes = 0

    return render(request, 'video/video_detail.html')

