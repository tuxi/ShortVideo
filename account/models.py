from django.contrib.auth.models import AbstractUser
from django.db import models
from ShortVideo.settings import (
    UPLOAD_AVATAR_AVATAR_ROOT,
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
                                                      ("female", "女")), default=u"female")
    # 地址
    address = models.CharField(max_length=100, default="")
    # 手机号
    phone = models.CharField(max_length=11, null=True, blank=True)
    # 用户头像
    image = models.ImageField(upload_to=UPLOAD_AVATAR_AVATAR_ROOT,
                              blank=True, null=True, verbose_name="用戶頭像")


    def get_uid(self):
        return self.id

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = verbose_name

    def __unicode__(self, ):
        return self.username


