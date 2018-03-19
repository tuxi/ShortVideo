from __future__ import absolute_import, unicode_literals

import errno
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage

import os
import subprocess

from celery import shared_task

from videokit.apps import VideokitConfig

@shared_task
def generate_video(file_name, source_file_name, options = []):
    base = getattr(settings, 'BASE_DIR', '')
    media_root = getattr(settings, 'MEDIA_ROOT', '')

    source_file = os.path.join(media_root, source_file_name)
    
    if not os.path.exists(source_file):
        raise IOError('%s does not exist.' % source_file)

    temp_file_dir = os.path.join(base, getattr(settings, 'VIDEOKIT_TEMP_DIR', VideokitConfig.VIDEOKIT_TEMP_DIR))
    temp_file = os.path.join(temp_file_dir, os.path.basename(file_name))

    if not os.path.exists(temp_file_dir):
        try:
           os.makedirs(temp_file_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    if not os.path.isdir(temp_file_dir):
        raise IOError('%s exists and is not a directory.' % temp_file_dir)

    process = subprocess.Popen(
        ['ffmpeg', '-i', source_file, '-y'] + options + [temp_file])

    process.wait()

    processed_file = os.path.join(base, media_root, file_name)
    f = File(open(temp_file, 'r'))
    default_storage.save(processed_file, f)
    f.close()

    os.remove(temp_file)
