# -*- coding: utf-8 -*-
# @Time    : 3/18/18 8:05 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from video.models import MediaItem
from ShortVideo.settings import PAGINATE_BY
from video.forms import MediaItemUploadForm


def index(request):
    template = 'video/video_index.html'

    media_items = MediaItem.objects.all()

    print(len(media_items))
    context = {
        'media_items' : media_items,
    }

    return render(request, template, context = context)


def upload(request):
    template = 'video/upload.html'
    upload_media_form = MediaItemUploadForm()
    if request.method == 'POST':
        upload_media_form = MediaItemUploadForm(request.POST, request.FILES)

        if upload_media_form.is_valid():
            video = request.FILES.get('video', None)

            if video:
                media_item = MediaItem(video = video)
                media_item.save()

                media_item.video_mp4.generate()
                media_item.video_ogg.generate()
                return HttpResponseRedirect(reverse('video:index'))

    context = {
        'upload_media_form' : upload_media_form,
    }

    return render(request, template, context)