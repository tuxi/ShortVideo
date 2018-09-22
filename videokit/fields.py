import errno

from celery.fixups import django
from django.conf import settings
from django.core.files import File
from django.db.models.fields.files import FieldFile
from django.db.models.fields.files import FileDescriptor
from django.db.utils import DataError

from datetime import datetime
import os.path
import subprocess

# from videokit.apps import VideokitConfig
# from videokit.tasks import generate_video

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

def get_start_time_str(seconds=0.0):
    '''
    将秒数转化为时间格式
    :param seconds:
    :return:
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


# 生成缩略图
def get_video_thumbnail(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)
    thumbnail_name = '%s%s' % (file.name, '.thumb.jpg')
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_name)
    if os.path.exists(thumbnail_path):
        return
    if os.path.isfile(path):
        # 获取从某个时间开始
        videoItem = file.instance
        start_time = videoItem.cover_start_second
        start_time = float(start_time)
        start_str = get_start_time_str(start_time)
        try:
            process = subprocess.Popen(
                ['ffmpeg', '-ss', start_str, '-i', path, '-frames', '1', '-y', thumbnail_path],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            if process.wait() == 0:
                return thumbnail_name

        except OSError:
            pass

    return ''

# 生成webp动图
def get_video_thumbnail_animated_webp(file):
    path = os.path.join(settings.MEDIA_ROOT, file.name)
    webp_name = '%s%s' % (file.name, '.animated.webp')
    webp_path = os.path.join(settings.MEDIA_ROOT, webp_name)
    if os.path.exists(webp_path):
        return
    if os.path.isfile(path):
        # 获取从某个时间开始
        videoItem = file.instance
        start_time = videoItem.cover_start_second
        duration = float(videoItem.cover_duration)
        if duration < 3.0:
            duration = 3.0
        start_time = float(start_time)
        start_str = get_start_time_str(start_time)
        try:
            # 执行ffmpeg命令 生成动图webp
            # ffmpeg -ss 00:00:01 -t 5 -i IMG_2021_pkutAEA.MOV -vcodec libwebp -lossless 0 -qscale 75 -preset default -loop 0 -vf scale=320:-1,fps=10 -an -vsync 0 output.webp
            process = subprocess.Popen(
                ['ffmpeg', '-ss', start_str, '-t', str(duration), '-i', path, '-vcodec', 'libwebp', '-lossless', '0', '-qscale', '75', '-preset', 'default', '-loop', '0', '-vf', 'scale=320:-1,fps=10', '-an', '-vsync', '0',
                  webp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if process.wait() == 0:
                return webp_name
        except OSError as e:
            pass
        finally:
            print("---")
    return ""
#
# # 截取视频前3秒 并转化为gif
# def get_video_thumbnail_gif(file):
#     '''
#     1、-ss 00：00：01表示从视频第一秒开始截取
#     2、- t 表示截图3秒钟的视频
#     3、-vf crop=iw:ih*2/3 表示截取视频的部分区域，其中宽为视频宽度，高为原视频的2/3
#     4、-r 7 表示每秒帧率为7帧
#     5、最后直接加上要生成的gif的路径就会把截取好的视频输出为gif了。
#     :param file: 视频文件
#     :return:
#     '''
#     path = os.path.join(settings.MEDIA_ROOT, file.name)
#     gif_name = '%s%s' % (file.name, '.thumb.gif')
#     gif_path = os.path.join(settings.MEDIA_ROOT, gif_name)
#     if os.path.exists(gif_path):
#         return
#     if os.path.isfile(path):
#         try:
#             # 执行ffmpeg命令
#             # ffmpeg -ss 00:00:01 -t 3 -i input视频 -vf crop=iw:ih*2/3 -s 320x240 -r 7 output.gif
#             process = subprocess.Popen(
#                 ['ffmpeg', '-ss', '00:00:01', '-t', '3', '-i', path, '-vf', 'crop=iw:ih*3/3', '-s', '640x480', '-r', '7', gif_path],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#             if process.wait() == 0:
#                 return gif_name
#         except OSError as e:
#             pass
#         finally:
#             print("___")
#     return ''

# 提取音頻文集aac
# def get_video_aac(file):
#
#     path = os.path.join(settings.MEDIA_ROOT, file.name)
#     aac_name = '%s%s' % (file.name, '.aac')
#     aac_path = os.path.join(settings.MEDIA_ROOT, aac_name)
#     if os.path.exists(aac_path):
#         return
#     if os.path.isfile(path):
#         try:
#             # 执行ffmpeg命令
#             # ffmpeg -i 3.mp4 -vn -y -acodec copy 3.aac
#             process = subprocess.Popen(
#                 ['ffmpeg', '-i', path, '-vn', '-y', '-acodec', 'copy',  aac_path],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#             if process.wait() == 0:
#                 return aac_path
#         except OSError as e:
#             print(str(e))
#
#     return ''


# 轉換爲mp4
def get_video_mp4(file):
    '''
    针对非MP4视频转换为mp4
    :param file:
    :return:
    '''
    path = os.path.join(settings.MEDIA_ROOT, file.name)
    if not os.path.exists(path):
        return ''
    # 如果该资源已经是MP4则不再转换
    # 获取后缀（文件类型）
    file_type = os.path.splitext(path)[-1][1:]
    if file_type and file_type.lower() == 'mp4':
        return path

    mp4_name = '%s%s' % (file.name, '.mp4')
    mp4_path = os.path.join(settings.MEDIA_ROOT, mp4_name)
    if os.path.exists(mp4_path):
        return
    if os.path.isfile(path):
        try:
            # 执行ffmpeg命令
            # ['-c:v', 'libtheora', '-c:a', 'libvorbis', '-q:v', '10', '-q:a', '6]
            # FFMPEG  -i  uploadfile/video/test.wmv -c:v libx264 -strict -2 uploadfile/mp4/test.mp4
            process = subprocess.Popen(
                ['ffmpeg', '-i', path, '-c:v', 'libx264', '-strict', '-2', mp4_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if process.wait() == 0:
                return mp4_path
        except OSError as e:
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

    # def _get_thumbnail_gif(self):
    #     return self._get_video_thumbnail_gif()
    #
    # gif = property(_get_thumbnail_gif)

    def _get_thumbnail_animated_wep(self):
        return self._get_video_thumbnail_animated_webp()

    animated_wep = property(_get_thumbnail_animated_wep)

    def _get_mp4(self):
        return self._get_video_mp4()

    mp4 = property(_get_mp4)

    # def _get_aac(self):
    #     return self._get_video_aac()
    #
    # aac = property(_get_aac)

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

    # def _get_video_thumbnail_gif(self):
    #     if not hasattr(self, '_thumbnail_gif_cache'):
    #         self._thumbnail_gif_cache = get_video_thumbnail_gif(self)
    #
    #     return self._thumbnail_gif_cache

    def _get_video_thumbnail_animated_webp(self):
        if not hasattr(self, '_thumbnail_animated_webp_cache'):
            self._thumbnail_animated_webp_cache = get_video_thumbnail_animated_webp(self)

        return self._thumbnail_animated_webp_cache

    def _get_video_mp4(self):
        if not hasattr(self, '_mp4_cache'):
            self._mp4_cache = get_video_mp4(self)

        return self._mp4_cache

    # def _get_video_aac(self):
    #     if not hasattr(self, '_aac_cache'):
    #         self._aac_cache = get_video_aac(self)
    #
    #     return self._aac_cache

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
            # self.field.update_gif_field(instance, force=True)
            self.field.update_animated_webp_field(instance, force=True)
            self.field.update_mp4_field(instance, force=True)
            # self.field.update_aac_field(instance, force=True)

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

        # if hasattr(self, '_thumbnail_gif_cache'):
        #     del self._thumbnail_gif_cache

        if hasattr(self, '_thumbnail_animated_webp_cache'):
            del self._thumbnail_animated_webp_cache

        if hasattr(self, '_mp4_cache'):
            del self._mp4_cache

        # if hasattr(self, '_aac_cache'):
        #     del self._aac_cache

        super(VideoFieldFile, self).delete(save)


# class VideoSpecFieldFile(VideoFieldFile):
#     def _require_file(self):
#         if not self.source_file:
#             raise ValueError('The \'%s\' attribute\'s source has no file associated with it.' % self.field_name)
#         else:
#             self.validate()
#
#     def delete(self, save = True):
#         if hasattr(self, '_generated_cache'):
#             del self._generated_cache
#
#         super(VideoSpecFieldFile, self).delete(save)
#
#     def validate(self):
#         return self.field.video_cache_backend.validate(self)
#
#     def invalidate(self):
#         return self.field.video_cache_backend.invalidate(self)
#
#     def clear(self):
#         return self.field.video_cache_backend.clear(self)
#
#     def generate(self):
#          if not self.generating() and not self.generated():
#             file_name = self.generate_file_name()
#
#             options = []
#             if self.field.format == 'mp4':
#                 options = ['-c:v', 'libx264', '-c:a', 'libfdk_aac', '-b:v', '1M', '-b:a', '128k']
#             elif self.field.format == 'ogg':
#                 options = ['-c:v', 'libtheora', '-c:a', 'libvorbis', '-q:v', '10', '-q:a', '6'] # ffmpeg -i 1.mp4  -acodec  libvorbis 1.ogg
#             elif self.field.format == 'webm':
#                 options = ['-c:v', 'libvpx', '-c:a', 'libvorbis', '-crf', '10', '-b:v', '1M']
#             try:
#                 self.name = file_name
#                 self.instance.save()
#             except DataError as e:
#                 print(file_name + str(e))
#
#             generate_video.delay(file_name, self.source_file.name, options = options)
#
#     def generating(self):
#         if self.name:
#             base = getattr(settings, 'BASE_DIR', '')
#             temp_file_dir = os.path.join(base, getattr(settings, 'VIDEOKIT_TEMP_DIR', VideokitConfig.VIDEOKIT_TEMP_DIR))
#             if not os.path.exists(temp_file_dir):
#                 try:
#                     os.makedirs(temp_file_dir)
#                 except OSError as e:
#                     if e.errno != errno.EEXIST:
#                         raise
#             temp_file = os.path.join(temp_file_dir, os.path.basename(self.name))
#
#             if os.path.exists(temp_file):
#                 return True
#
#         return False
#
#     def generate_file_name(self):
#         cachefile_dir = getattr(settings, 'VIDEOKIT_CACHEFILE_DIR', VideokitConfig.VIDEOKIT_CACHEFILE_DIR)
#         dir = os.path.join(cachefile_dir, os.path.splitext(self.source_file.name)[0])
#         file_string = '%s%s%s' % (self.source_file.name, self.field.format, str(datetime.now()))
#         try:
#             import md5
#             hash = md5.new(file_string).hexdigest()
#         except ImportError:
#             from hashlib import md5
#             hash = md5(file_string.encode()).hexdigest()
#
#         file_name = hash + '.' + self.field.format
#
#         return os.path.join(dir, file_name)
#
#     def generated(self):
#         if hasattr(self, '_generated_cache'):
#             return self._generated_cache
#         else:
#             if self.name:
#                 if self.storage.exists(self.name):
#                     self._generated_cache = True
#                     return True
#
#         return False
#
#     @property
#     def source_file(self):
#         source_field_name = getattr(self.field, 'source', None)
#         if source_field_name:
#             return getattr(self.instance, source_field_name)
#         else:
#             return None

class VideoSpecFileDescriptor(VideoFileDescriptor):
    pass
