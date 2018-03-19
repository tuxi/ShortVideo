from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('video.urls', namespace='video', app_name='video')),
]

from django.conf import settings
if settings.DEBUG:
    # 配置上传按访问处理函数
    # 如果使用settings.MEDIA_ROOT,那么会上传到media/下，因为settings中的MEDIA_ROOT路径为../media
    from django.views.static import serve

    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    )