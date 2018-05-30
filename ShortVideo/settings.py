"""
Django settings for ShortVideo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import base64
import os

# 项目的根目录
# 简化后面的操作
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's$-9&3j^=+$&^wi=hu4q%$2x#(6giqtendmaa1a=7ozma4zsuh'
JWT_SECRET = base64.b64encode(b'ScaredCherriesEatSurelySimpleVulcansParticipateIntensely')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'video.apps.VideoConfig',
    'videokit.apps.VideokitConfig',
    'account.apps.AccountConfig',
    'gunicorn',
    'imagekit',
)

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 加上这个之后，django就会自动给MEDIA_URL 注册到thml当中去，如果不这么配置，实际上是取不到MEDIA_URL 这个值的
                # 完成上面的配置之后，发现还是没显示出我们的图片，是因为我们没有指定访问这个URL {{ MEDIA_URL }}{{ org.image }}时应该去哪去这个文件，在urls.py文件中进行以下设置：
                'django.template.context_processors.media',
            ],
            'debug': DEBUG,#在settings.py 中把以TEMPLATE_开头的设置信息，全都加到一个TEMPLATES中。因为到户都是Template相关的设置，那为什么不把他们都放在一起呢？？
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shortvideo',  # 数据库名称
        'USER':'root', # 数据库用户名
        'PASSWORD': 'root',  # 数据库密码
        'HOST': '127.0.0.1', # 数据库主机，留空默认为localhost
        'PORT': 3306, # 数据库端口
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }
]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# 语言
LANGUAGE_CODE = 'zh-hans'

# 时区
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

ROOT_URLCONF = 'ShortVideo.urls'
AUTH_USER_MODEL = 'account.UserProfile'

WSGI_APPLICATION = 'ShortVideo.wsgi.application'

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.abspath(os.path.join(SITE_ROOT, '../'))

STATIC_ROOT = os.path.join(SITE_ROOT, 'collectedstatic')

# 给静态文件url一个后，在templates里用到的。
# 映射到静态文件的url
STATIC_URL = '/static/'
STATICFILES = os.path.join(BASE_DIR, 'static')

MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR, 'media')

if not os.path.isdir(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)



# 分页
PAGINATE_BY = 20


######################################################################
USER_AVATAR_URL = 'avatar'
USER_AVATAR_ROOT = os.path.join(MEDIA_ROOT, 'avatar')
if not os.path.isdir(USER_AVATAR_ROOT):
    os.mkdir(USER_AVATAR_ROOT)

