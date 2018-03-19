from __future__ import unicode_literals

from django.apps import AppConfig


class VideokitConfig(AppConfig):
    name = 'videokit'
    DEFAULT_VIDEO_CACHE_BACKEND = 'videokit.cache.VideoCacheBackend'
    VIDEOKIT_CACHEFILE_DIR = 'CACHE/videos'
    VIDEOKIT_TEMP_DIR = 'videokit-temp'
    VIDEOKIT_SUPPORTED_FORMATS = ['mp4', 'ogg', 'webm']
    VIDEOKIT_DEFAULT_FORMAT = 'mp4'
