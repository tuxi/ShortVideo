# -*- coding: utf-8 -*-
# @Time    : 3/18/18 8:05 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : urls.py
# @Software: PyCharm

from __future__ import unicode_literals
from account.models import UserProfile
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.db.models import Avg, Count, Func
from ShortVideo.settings import BASE_DIR
from videokit.models import VideoField
from django.core.validators import MinLengthValidator
from dss.Serializer import serializer
import json
import os

def upload_to(instance, filename):
    return 'media_items{filename}'.format(filename=filename)

class VideoItem(models.Model):
    """媒体文件"""
    STATUS_CHOICES = (
        ('d', '審核'),
        ('p', '发表'),
    )
    COMMENT_STATUS = (
        ('o', '打开'),
        ('c', '关闭'),
    )
    video = VideoField(upload_to=upload_to,
                       width_field='video_width', height_field='video_height',
                       rotation_field='video_rotation',
                       mimetype_field='video_mimetype',
                       duration_field='video_duration',
                       thumbnail_field='video_thumbnail',
                       animated_webp_field='video_animated_webp',
                       #gif_field='video_gif',
                       mp4_field='video_mp4',
                       #aac_field='video_sound',
                        cover_duration_filed='cover_duration',
                       cover_start_second_filed='cover_start_second'
                       )
    video_width = models.IntegerField(null=True, blank=True)
    video_height = models.IntegerField(null=True, blank=True)
    video_rotation = models.FloatField(null=True, blank=True)
    video_mimetype = models.CharField(max_length=32, null=True, blank=True)
    # 视频时长
    video_duration = models.IntegerField(null=True, blank=True)
    # 视频缩略图
    video_thumbnail = models.ImageField(null=True, blank=True)
    # 视频前3秒的gif图
    #video_gif = models.ImageField(null=True, blank=True)
    video_mp4 = models.FileField(blank=True, verbose_name='mp4', null=True)
    #video_sound = models.FileField(blank=True, verbose_name='sound', null=True)

    # 视频前10秒的wep动图，和gif的功能基本相同，使用webp是为了优化客户端流量及性能
    video_animated_webp = models.ImageField(null=True, blank=True)
    # 封面的起始时间，决定webp从视频的哪里开始显示
    cover_start_second = models.FloatField(null=True, blank=True)
    # 封面的长度，决定webp的播放时间
    cover_duration = models.FloatField(null=True, blank=True)
    title = models.CharField('视频名称', max_length=200, unique=False)
    describe = models.TextField('描述')
    upload_time = models.DateTimeField('上传时间', default=timezone.now)
    pub_time = models.DateTimeField('发布时间', blank=True, null=True)
    views = models.PositiveIntegerField('观看次数', default=0)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE, blank=True, null=True)
    comment_status = models.CharField('评论状态', max_length=1, choices=COMMENT_STATUS, default='o')
    status = models.CharField('视频状态', max_length=1, choices=STATUS_CHOICES, default='p')

    def __str__(self):
        return self.title + self.describe

    class Meta:
        ordering = ['-pub_time']
        verbose_name = "视频"
        verbose_name_plural = verbose_name
        get_latest_by = 'upload_time'



    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        comment_list = Comment.objects.filter(video=self).values()
        return comment_list

    def get_comment_num(self):
        return len(self.comment_list())

    # @property
    # def video_gif_url(self):
    #     if self.video_gif and hasattr(self.video_gif, 'url'):
    #         return self.video_gif.url
    #     return ""

    @property
    def video_mp4_url(self):
        if self.video_mp4 and hasattr(self.video_mp4, 'url'):
            url = self.video_mp4.url
            if BASE_DIR in url:
                url = url.split(BASE_DIR)[1]
                return url
        return None

    # @property
    # def video_sound_url(self):
    #     if self.video_sound and hasattr(self.video_sound, 'url'):
    #         url = self.video_sound.url
    #         if BASE_DIR in url:
    #             url = url.split(BASE_DIR)[1]
    #             return url
    #     return ""

    @property
    def video_thumbnail_url(self):
        if self.video_thumbnail and hasattr(self.video_thumbnail, 'url'):
            return self.video_thumbnail.url
        return None

    @property
    def video_url(self):
        if self.video and hasattr(self.video, 'url'):
            return self.video.url
        return None

    @property
    def video_animated_webp_url(self):
        if self.video_animated_webp and hasattr(self.video_animated_webp, 'url'):
            return self.video_animated_webp.url
        return None

    def to_dict(self):
        # 序列化model, foreign=True,并且序列化主键对应的mode, exclude_attr 列表里的字段
        dict = serializer(data=self, foreign=False, exclude_attr=('password', 'video_thumbnai', 'video_mp4', 'video_animated_webp' , 'video'))
        user = UserProfile.objects.filter(pk=self.user_id).first()
        user_dict = user.to_dict()
        dict['author'] = user_dict
        dict['video'] = self.video_url
        dict['video_thumbnail'] = self.video_thumbnail_url
        dict['video_mp4'] = self.video_mp4_url
        #dict['video_sound'] = self.video_sound_url
        dict['video_animated_webp'] = self.video_animated_webp_url
        #dict['video_gif'] = self.video_gif_url

        ############ 獲取該視頻的評級
        r = Rating.objects.filter(video=self).values('rating').aggregate(
            avg_rating=Avg('rating'),
            rating_count=Count('rating')
        )
        avg_rating = r['avg_rating']
        rating_count = r['rating_count']

        # 獲取該視頻的所有評論
        c = self.comment_list()

        dict['rating'] = {
            'avg': '{:.1f}'.format(avg_rating) if avg_rating is not None else None,
            'count': rating_count
        }
        dict['comments'] = list(c)
        return dict

    def to_json(self):
        dict = self.to_dict()
        return json.dumps(dict)

    # 将一组VideoItem集合转换为一组字典集合
    @classmethod
    def to_dict_list(cls, video_list):
        videos = []
        for video in video_list:
            try:
                video_dict = video.to_dict()
                videos.append(video_dict)
            except ValueError as e:
                print(e.__str__())
        return videos

    def rollback_resource(self):
        '''
        清空视频  比如保存失败
        :return:
        '''
        list = []
        videoMp4Path = self.video_mp4_url
        if videoMp4Path is not None:
            list.append(videoMp4Path)
        videoPath = self.video_url
        if videoPath is not None:
            list.append(videoPath)
        webpPath = self.video_animated_webp_url
        if webpPath is not None:
            list.append(webpPath)
        thumbnailPath = self.video_thumbnail_url
        if thumbnailPath is not None:
            list.append(thumbnailPath)

        for item in list:
            path = item
            if BASE_DIR not in item:
                path = BASE_DIR + item
            if not os.path.exists(path):
                return
            if not os.path.isfile(path):
                return
            os.remove(path)

class Category(models.Model):
    """视频分类"""
    name = models.CharField('分类名', max_length=30, unique=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def to_dict(self):
        dict = serializer(data=self, foreign=True)
        return dict

    def to_json(self):
        return serializer(data=self, output_type='json', foreign=True)

class Likes(models.Model):
    video = models.ForeignKey(VideoItem,verbose_name='视频',on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name='时间',auto_now_add=True)

    def __str__(self):
        return str(self.video)

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = verbose_name

    def to_dict(self):
        dict = serializer(data=self, foreign=True)
        return dict

    def to_json(self):
        return serializer(data=self, output_type='json', foreign=True)

class Rating(models.Model):
    video = models.ForeignKey(VideoItem, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    username = models.CharField(max_length=100, validators=[MinLengthValidator(1)])

    def __str__(self):
        return 'ID: %s | Vote: %s' % (self.video, self.rating)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Rating, self).save(*args, **kwargs)

    def to_dict(self):
        dict = serializer(data=self, foreign=True)
        return dict

    def to_json(self):
        return serializer(data=self, output_type='json', foreign=True)

class Comment(models.Model):
    video = models.ForeignKey(VideoItem, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, validators=[MinLengthValidator(1)])
    body = models.TextField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Comment, self).save(*args, **kwargs)

    def to_dict(self):
        dict = serializer(data=self, foreign=True)
        return dict

    def to_json(self):
        return serializer(data=self, output_type='json', foreign=False)