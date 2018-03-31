from __future__ import unicode_literals

from django.apps import AppConfig
from ShortVideo.settings import MEDIA_URL

class VideokitConfig(AppConfig):
    name = 'videokit'
    DEFAULT_VIDEO_CACHE_BACKEND = 'videokit.cache.VideoCacheBackend'
    VIDEOKIT_CACHEFILE_DIR = 'media/CACHE/videos'
    VIDEOKIT_TEMP_DIR =  'media/videotemp'
    VIDEOKIT_SUPPORTED_FORMATS = ['mp4', 'ogg', 'webm']
    VIDEOKIT_DEFAULT_FORMAT = 'mp4'
