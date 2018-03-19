from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShortVideo.settings')

app = Celery('ShortVideo')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.broker_url = 'redis://localhost:6379/0'

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
