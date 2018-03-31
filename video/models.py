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
from ShortVideo import settings
from videokit.models import VideoField, VideoSpecField
from django.core.validators import MinLengthValidator
from dss.Serializer import serializer
import json

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
                       )
    video_width = models.IntegerField(null=True, blank=True)
    video_height = models.IntegerField(null=True, blank=True)
    video_rotation = models.FloatField(null=True, blank=True)
    video_mimetype = models.CharField(max_length=32, null=True, blank=True)
    # 视频时长
    video_duration = models.IntegerField(null=True, blank=True)
    # 视频缩略图
    video_thumbnail = models.ImageField(null=True, blank=True)
    video_mp4 = VideoSpecField(source = 'video', format = 'mp4')
    video_ogg = VideoSpecField(source='video', format='ogg')
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

    def video_spects_generated(self):
        if self.video_mp4.generated() and self.video_ogg.generated():
            return True
        return False

    # def get_absolute_url(self):
    #     return reverse('video:detail', kwargs={
    #         'article_id': self.id,
    #     })


    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        comment_list = Comment.objects.filter(video=self).values()
        return comment_list

    def get_comment_num(self):
        return len(self.comment_list())

    def to_dict(self):
        # 序列化model, foreign=True,并且序列化主键对应的mode, exclude_attr 列表里的字段
        dict = serializer(data=self, foreign=True, exclude_attr=('password', 'image'))
        dict['video'] = self.video.url
        dict['video_thumbnail'] = self.video_thumbnail.url
        dict['video_mp4'] = self.video_mp4.url
        dict['video_ogg'] = self.video_ogg.url


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
            videos.append(video.to_dict())
        return videos


class Category(models.Model):
    """视频分类"""
    name = models.CharField('分类名', max_length=30, unique=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    # def get_absolute_url(self):
    #     url = reverse('blog:category_detail', kwargs={'category_name': self.slug})
    #     return url

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