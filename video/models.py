# -*- coding: utf-8 -*-
# @Time    : 3/18/18 8:05 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from __future__ import unicode_literals
from django.db import models
from videokit.models import VideoField, VideoSpecField

def upload_to(instance, filename):
    return 'media_items{filename}'.format(filename=filename)

class MediaItem(models.Model):
    video = VideoField(upload_to=upload_to,
                       width_field='video_width', height_field='video_height',
                       rotation_field='video_rotation',
                       mimetype_field='video_mimetype',
                       duration_field='video_duration',
                       thumbnail_field='video_thumbnail',
                       )
    video_width = models.IntegerField(null=True, blank=True)
    video_height = models.IntegerField(null=True, blank=True)
    video_rotation = models.FloatField(null=True, blank=True)
    video_mimetype = models.CharField(max_length=32, null=True, blank=True)
    video_duration = models.IntegerField(null=True, blank=True)
    video_thumbnail = models.ImageField(null=True, blank=True)
    video_mp4 = VideoSpecField(source = 'video', format = 'mp4')
    video_ogg = VideoSpecField(source='video', format='ogg')

    def __unicode__(self):
        return self.video.name

    def video_spects_generated(self):
        if self.video_mp4.generated() and self.video_ogg.generated():
            return True
        return False
