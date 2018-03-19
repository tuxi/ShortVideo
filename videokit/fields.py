from django.conf import settings
from django.core.files import File
from django.db.models.fields.files import FieldFile
from django.db.models.fields.files import FileDescriptor

from datetime import datetime
import os.path
import subprocess

from videokit.apps import VideokitConfig
from videokit.tasks import generate_video

def get_video_dimensions(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)

    if os.path.isfile(path):
        try:
            process = subprocess.Popen(
                ['mediainfo', '--Inform=Video;%Width%', path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            stdout, stderr = process.communicate()
            if process.wait() == 0:
                width = int(stdout.decode('utf8').strip(' \t\n\r'))
            else:
                return (0,0)

            process = subprocess.Popen(
                ['mediainfo', '--Inform=Video;%Height%', path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            stdout, stderr = process.communicate()
            if process.wait() == 0:
                height = int(stdout.decode('utf8').strip(' \t\n\r'))
            else:
                return (None, None)

            return (width, height)
        except OSError:
            pass

    return (None, None)

def get_video_rotation(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)

    if os.path.isfile(path):
        try:
            process = subprocess.Popen(
                ['mediainfo', '--Inform=Video;%Rotation%', path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            stdout, stderr = process.communicate()
            if process.wait() == 0:
                try:
                    rotation = float(stdout.decode('utf8').strip(' \t\n\r'))
                except ValueError:
                    rotation = 0.0

                return rotation
        except OSError:
            pass

    return 0.0

def get_video_mimetype(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)

    if os.path.isfile(path):
        try:
            process = subprocess.Popen(
                ['mediainfo', '--Inform=Video;%InternetMediaType%', path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            stdout, stderr = process.communicate()
            if process.wait() == 0:
                mimetype = stdout.decode('utf8').strip(' \t\n\r')
                if mimetype == 'video/H264':
                    mimetype = 'video/mp4'

                if mimetype == '':
                    mimetype = 'video/mp4'
                return mimetype
        except OSError:
            pass

    return ''

def get_video_duration(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)

    if os.path.isfile(path):
        try:
            process = subprocess.Popen(
                ['mediainfo', '--Inform=Video;%Duration%', path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            stdout, stderr = process.communicate()
            if process.wait() == 0:
                try:
                    duration = int(stdout.decode('utf8').strip(' \t\n\r'))
                except ValueError:
                    duration = 0

                return duration
        except OSError:
            pass

    return 0

def get_video_thumbnail(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)
    thumbnail_name = '%s%s' % (file.name, '.thumb.jpg')
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_name)

    if os.path.isfile(path):
        try:
            process = subprocess.Popen(
                ['ffmpeg', '-i', path, '-frames', '1', '-y', thumbnail_path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            if process.wait() == 0:
                return thumbnail_name

        except OSError:
            pass

    return ''

class VideoFile(File):
    def _get_width(self):
        return self._get_video_dimensions()[0]

    width = property(_get_width)

    def _get_height(self):
        return self._get_video_dimensions()[1]

    height = property(_get_height)

    def _get_rotation(self):
        return self._get_video_rotation()

    rotation = property(_get_rotation)

    def _get_mimetype(self):
        return self._get_video_mimetype()

    mimetype = property(_get_mimetype)

    def _get_duration(self):
        return self._get_video_duration()

    duration = property(_get_duration)

    def _get_thumbnail(self):
        return self._get_video_thumbnail()

    thumbnail = property(_get_thumbnail)

    def _get_video_dimensions(self):
        if not hasattr(self, '_dimensions_cache'):
            self._dimensions_cache = get_video_dimensions(self)

        return self._dimensions_cache

    def _get_video_rotation(self):
        if not hasattr(self, '_rotation_cache'):
            self._rotation_cache = get_video_rotation(self)

        return self._rotation_cache

    def _get_video_mimetype(self):
        if not hasattr(self, '_mimetype_cache'):
            self._mimetype_cache = get_video_mimetype(self)

        return self._mimetype_cache

    def _get_video_duration(self):
        if not hasattr(self, '_duration_cache'):
            self._duration_cache = get_video_duration(self)

        return self._duration_cache

    def _get_video_thumbnail(self):
        if not hasattr(self, '_thumbnail_cache'):
            self._thumbnail_cache = get_video_thumbnail(self)

        return self._thumbnail_cache

class VideoFileDescriptor(FileDescriptor):
    def __set__(self, instance, value):
        previous_file = instance.__dict__.get(self.field.name)
        super(VideoFileDescriptor, self).__set__(instance, value)

        if previous_file is not None:
            self.field.update_dimension_fields(instance, force = True)
            self.field.update_rotation_field(instance, force = True)
            self.field.update_mimetype_field(instance, force = True)
            self.field.update_duration_field(instance, force = True)
            self.field.update_thumbnail_field(instance, force = True)

class VideoFieldFile(VideoFile, FieldFile):
    def delete(self, save = True):
        if hasattr(self, '_dimensions_cache'):
            del self._dimensions_cache

        if hasattr(self, '_rotation_cache'):
            del self._rotation_cache

        if hasattr(self, '_mimetype_cache'):
            del self._mimetype_cache

        if hasattr(self, '_duration_cache'):
            del self._duration_cache

        if hasattr(self, '_thumbnail_cache'):
            del self._thumbnail_cache

        super(VideoFieldFile, self).delete(save)


class VideoSpecFieldFile(VideoFieldFile):
    def _require_file(self):
        if not self.source_file:
            raise ValueError('The \'%s\' attribute\'s source has no file associated with it.' % self.field_name)
        else:
            self.validate()

    def delete(self, save = True):
        if hasattr(self, '_generated_cache'):
            del self._generated_cache

        super(VideoSpecFieldFile, self).delete(save)

    def validate(self):
        return self.field.video_cache_backend.validate(self)

    def invalidate(self):
        return self.field.video_cache_backend.invalidate(self)

    def clear(self):
        return self.field.video_cache_backend.clear(self)

    def generate(self):
         if not self.generating() and not self.generated():
            file_name = self.generate_file_name()

            options = []
            if self.field.format == 'mp4':
                options = ['-c:v', 'libx264', '-c:a', 'libfdk_aac', '-b:v', '1M', '-b:a', '128k']
            elif self.field.format == 'ogg':
                options = ['-c:v', 'libtheora', '-c:a', 'libvorbis', '-q:v', '10', '-q:a', '6']
            elif self.field.format == 'webm':
                options = ['-c:v', 'libvpx', '-c:a', 'libvorbis', '-crf', '10', '-b:v', '1M']

            self.name = file_name
            self.instance.save()

            generate_video.delay(file_name, self.source_file.name, options = options)

    def generating(self):
        if self.name:
            base = getattr(settings, 'BASE_DIR', '')
            temp_file_dir = os.path.join(base, getattr(settings, 'VIDEOKIT_TEMP_DIR', VideokitConfig.VIDEOKIT_TEMP_DIR))
            temp_file = os.path.join(temp_file_dir, os.path.basename(self.name))

            if os.path.exists(temp_file):
                return True

        return False

    def generate_file_name(self):
        cachefile_dir = getattr(settings, 'VIDEOKIT_CACHEFILE_DIR', VideokitConfig.VIDEOKIT_CACHEFILE_DIR)
        dir = os.path.join(cachefile_dir, os.path.splitext(self.source_file.name)[0])
        file_string = '%s%s%s' % (self.source_file.name, self.field.format, str(datetime.now()))
        try:
            import md5
            hash = md5.new(file_string).hexdigest()
        except ImportError:
            from hashlib import md5
            hash = md5(file_string.encode()).hexdigest()

        file_name = hash + '.' + self.field.format

        return os.path.join(dir, file_name)

    def generated(self):
        if hasattr(self, '_generated_cache'):
            return self._generated_cache
        else:
            if self.name:
                if self.storage.exists(self.name):
                    self._generated_cache = True
                    return True

        return False

    @property
    def source_file(self):
        source_field_name = getattr(self.field, 'source', None)
        if source_field_name:
            return getattr(self.instance, source_field_name)
        else:
            return None

class VideoSpecFileDescriptor(VideoFileDescriptor):
    pass
