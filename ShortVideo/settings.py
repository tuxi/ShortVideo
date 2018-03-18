"""
Django settings for ShortVideo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's$-9&3j^=+$&^wi=hu4q%$2x#(6giqtendmaa1a=7ozma4zsuh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

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
        },
    },
]


ROOT_URLCONF = 'ShortVideo.urls'

WSGI_APPLICATION = 'ShortVideo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# 数据库配置
MYDB = {
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shortvideo',  # 数据库名称
        'USER':'root', # 数据库用户名
        'PASSWORD': 'root',  # 数据库密码
        'HOST': '127.0.0.1', # 数据库主机，留空默认为localhost
        'PORT': 3306, # 数据库端口
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db/db.sqlite3').replace('\\', '/'),
    }
}


# 数据库配置
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': MYDB.get('mysql')
}

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

STATIC_URL = '/static/'
