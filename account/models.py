from django.contrib.auth.models import AbstractUser
from django.db import models
from dss.Serializer import serializer
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from ShortVideo.settings import (
    USER_AVATAR_URL
)
# Create your models here.

class UserProfile(AbstractUser):
    """
    继承AbstrcatUser，生成自己的User表, username爲用戶唯一標示
    """
    # 昵称
    nickname = models.CharField(max_length=50, verbose_name=u"昵称", default="")
    # 生日
    birday = models.DateField(verbose_name=u"生日", null=True, blank=True)
    # 性别
    gender = models.CharField(max_length=10, choices=(("male", "男"),
                                                      ("female", "女")), default=u"female", blank=True, null=True)
    # 地址
    address = models.CharField(max_length=100, blank=True, null=True,default="")
    # 手机号
    phone = models.CharField(max_length=11, null=True, blank=True)
    # 用户头像
    # ProcessedImageField和django的ImageFIeld相似，区别是前者可以处理图片，生成指定大小的缩略图，更多详细的说明请查看imagekit官方文档。
    avatar = ProcessedImageField(upload_to=USER_AVATAR_URL, blank=True, default='avatar/default.png', verbose_name='头像',
                                 processors=[ResizeToFill(640,640)],
                                 format='JPEG',
                                 options={'quality':100})
    # 用戶簡介
    summary = models.CharField(max_length=300, blank=True, null=True, verbose_name="用戶簡介")

    # 个人主页 cover image, 后台未做任何处理, 由前台处理cover尺寸
    cover = models.ImageField(upload_to=USER_AVATAR_URL,
                              blank=True, null=True,
                              verbose_name="cover image")

    @property
    def cover_url(self):
        if self.cover and hasattr(self.cover, 'url'):
            return self.cover.url
        return ""
    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return ""

    def save(self, *args, **kwargs):
        if len(self.avatar.name.split('/')) == 1:
            self.avatar.name = self.username + '/' + self.avatar.name
        super(UserProfile, self).save(*args, **kwargs)

    def get_uid(self):
        return self.id

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = verbose_name

    def __unicode__(self, ):
        return self.username

    def to_dict(self):
        # 序列化model, foreign=True,并且序列化主键对应的model, exclude_attr 列表里的字段
        dict = serializer(data=self, foreign=True, exclude_attr=('password', 'backend', 'cover', 'avatar'))
        cover_url = self.cover_url
        dict["cover"] = cover_url
        avarar_url = self.avatar_url
        dict["avatar"] = avarar_url


        return dict
