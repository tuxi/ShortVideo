from django.urls import path
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',  include('video.urls', namespace='video')),
]