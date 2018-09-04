# -*- coding: utf-8 -*-
# @Time    : 3/20/18 7:32 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : jwt_authentication.py
# @Software: PyCharm

from django.core.exceptions import PermissionDenied
import jwt
from django.conf import settings
from account import utils

# since I am using the middleware on a per-view basis I need to define the process_request | process_response
# methods and not the __init__ | __call__ ones
# http://agiliq.com/blog/2015/07/understanding-django-middlewares/
# https://docs.djangoproject.com/en/1.11/ref/utils/#django.utils.decorators.decorator_from_middleware

class JwtAuthentication(object):
    def process_request(self, request):
        token = utils.get_auth_token(request)
        if token:
            try:
                payload = jwt.decode(token, settings.JWT_SECRET)
            except jwt.ExpiredSignatureError:
                raise PermissionDenied
            except Exception as e:
                raise PermissionDenied
            # 授予權限 確定登錄成功
            return None
        else:
            raise PermissionDenied



# "standard" middleware
# https://docs.djangoproject.com/en/1.11/topics/http/middleware/#writing-your-own-middleware
# and then add on the end of settings.py > MIDDLEWARE as movies.middlewares...
# middleware will be applied to each view

# other interesting link, middlewares with arguments or to decorate methods
# https://docs.djangoproject.com/en/1.11/ref/utils/#module-django.utils.decorators