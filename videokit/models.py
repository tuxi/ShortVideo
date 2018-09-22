from __future__ import unicode_literals

from django.db import models
from django.db.models import signals
from django.core import checks

import subprocess
from videokit.fields import VideoFieldFile
from videokit.fields import VideoFileDescriptor
from videokit.forms import VideoField as VideoFormField


class VideoField(models.FileField):
    attr_class = VideoFieldFile
    descriptor_class = VideoFileDescriptor
    description = 'Video'
    
    def __init__(   self, verbose_name = None, name = None, 
                    width_field = None, height_field = None, 
                    rotation_field = None,
                    mimetype_field = None,
                    duration_field = None,
                    thumbnail_field = None,
                    gif_field = None,
                    animated_webp_field = None,
                    mp4_field = None,
                    aac_field = None,
                    cover_duration_filed = None,
                    cover_start_second_filed = None,
                    **kwargs):
        self.width_field = width_field
        self.height_field = height_field
        self.rotation_field = rotation_field
        self.mimetype_field = mimetype_field
        self.duration_field = duration_field
        self.thumbnail_field = thumbnail_field
        #self.gif_field = gif_field
        self.animated_webp_field = animated_webp_field
        self.mp4_field = mp4_field
        #self.aac_field = aac_field
        self.cover_duration_filed = cover_duration_filed
        self.cover_start_second_filed = cover_start_second_filed
        super(VideoField, self).__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        errors = super(VideoField, self).check(**kwargs)
        errors.extend(self._check_video_utils_installed())
        return errors

    def _check_video_utils_installed(self):
        command = 'which ffmpeg'
        response = subprocess.call(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if response != 0:
            return [        
                checks.Error(
                    'ffmpeg is not installed',
                    hint = ('Install FFMPEG from https://www.ffmpeg.org'),
                    obj = self,
                )
            ]

        command = 'which mediainfo'
        response = subprocess.call(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if response != 0:
            return [        
                checks.Error(
                    'mediainfo is not installed',
                    hint = ('Install Mediainfo from https://mediaarea.net'),
                    obj = self,
                )
            ]

        return []
        
    def deconstruct(self):
        name, path, args, kwargs = super(VideoField, self).deconstruct()
        if self.width_field:
            kwargs['width_field'] = self.width_field

        if self.height_field:
            kwargs['height_field'] = self.height_field

        if self.rotation_field:
            kwargs['rotation_field'] = self.rotation_field

        if self.mimetype_field:
            kwargs['mimetype_field'] = self.mimetype_field

        if self.duration_field:
            kwargs['duration_field'] = self.duration_field

        if self.thumbnail_field:
            kwargs['thumbnail_field'] = self.thumbnail_field

        #if self.gif_field:
        #    kwargs['gif_field'] = self.gif_field

        if self.animated_webp_field:
            kwargs['animated_webp_field'] = self.animated_webp_field

        if self.mp4_field:
            kwargs['mp4_field'] = self.mp4_field

        #if hasattr(self, "aac_field"):
         #   if self.aac_field:
          #      kwargs['aac_field'] = self.aac_field

        if self.cover_duration_filed:
            kwargs['cover_duration_filed'] = self.cover_duration_filed

        if self.cover_start_second_filed:
            kwargs['cover_start_second_filed'] = self.cover_start_second_filed


        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super(VideoField, self).contribute_to_class(cls, name, **kwargs)

        if not cls._meta.abstract:
            signals.post_init.connect(self.update_dimension_fields, sender = cls)
            signals.post_init.connect(self.update_cover_fields, sender=cls)
            signals.post_init.connect(self.update_rotation_field, sender = cls)
            signals.post_init.connect(self.update_mimetype_field, sender = cls)
            signals.post_init.connect(self.update_duration_field, sender = cls)
            signals.post_init.connect(self.update_thumbnail_field, sender = cls)
           # signals.post_init.connect(self.update_gif_field, sender= cls)
            signals.post_init.connect(self.update_animated_webp_field, sender=cls)

            signals.post_init.connect(self.update_mp4_field, sender=cls)
            #signals.post_init.connect(self.update_aac_field, sender=cls)

    def update_dimension_fields(self, instance, force = False, *args, **kwargs):
        has_dimension_fields = self.width_field or self.height_field
        if not has_dimension_fields:
            return

        file = getattr(instance, self.attname)

        if not file and not force:
            return

        dimension_fields_filled = not(
            (self.width_field and not getattr(instance, self.width_field))
            or (self.height_field and not getattr(instance, self.height_field)))

        if dimension_fields_filled and not force:
            return

        if file:
            width = file.width
            height = file.height
        else:
            width = None
            height = None

        if self.width_field:
            setattr(instance, self.width_field, width)
        if self.height_field:
            setattr(instance, self.height_field, height)

    def update_rotation_field(self, instance, force = False, *args, **kwargs):
        has_rotation_field = self.rotation_field
        if not has_rotation_field:
            return

        file = getattr(instance, self.attname)

        if not file and not force:
            return

        rotation_field_filled = not(self.rotation_field and not getattr(instance, self.rotation_field))

        if rotation_field_filled and not force:
            return

        if file:
            rotation = file.rotation
        else:
            rotation = None

        if self.rotation_field:
            setattr(instance, self.rotation_field, rotation)

    def update_mimetype_field(self, instance, force = False, *args, **kwargs):
        has_mimetype_field = self.mimetype_field
        if not has_mimetype_field:
            return

        file = getattr(instance, self.attname)
    
        if not file and not force:
            return

        mimetype_field_filled = not(self.mimetype_field and not getattr(instance, self.mimetype_field))
        
        if mimetype_field_filled and not force:
            return

        if file:
            mimetype = file.mimetype
        else:
            mimetype = None

        if self.mimetype_field:
            setattr(instance, self.mimetype_field, mimetype)
        
    def update_duration_field(self, instance, force = False, *args, **kwargs):
        has_duration_field = self.duration_field
        if not has_duration_field:
            return

        file = getattr(instance, self.attname)
        
        if not file and not force:
            return

        duration_field_filled = not(self.duration_field and not getattr(instance, self.duration_field))

        if duration_field_filled and not force:
            return

        if file:
            duration = file.duration
        else:
            duration = None

        if self.duration_field:
            setattr(instance, self.duration_field, duration)
    
    def update_thumbnail_field(self, instance, force = False, *args, **kwargs):
        has_thumbnail_field = self.thumbnail_field
        if not has_thumbnail_field:
            return

        file = getattr(instance, self.attname)

        if not file and not force:
            return

        thumbnail_field_filled = not(self.thumbnail_field and not getattr(instance, self.thumbnail_field))

        if thumbnail_field_filled and not force:
            return

        if file:
            thumbnail = file.thumbnail
        else:
            thumbnail = None

        if self.thumbnail_field:
            setattr(instance, self.thumbnail_field, thumbnail)
    #
    # def update_gif_field(self, instance, force = False, *args, **kwargs):
    #     has_gif_field = self.gif_field
    #     if not has_gif_field:
    #         return
    #
    #     file = getattr(instance, self.attname)
    #
    #     if not file and not force:
    #         return
    #
    #     gif_field_filled = not(self.gif_field and not getattr(instance, self.gif_field))
    #
    #     if gif_field_filled and not force:
    #         return
    #
    #     if file:
    #         gif = file.gif
    #     else:
    #         gif = None
    #     if self.gif_field:
    #         setattr(instance, self.gif_field, gif)

    def update_animated_webp_field(self, instance, force = False, *args, **kwargs):
        has_animated_webp_field = self.animated_webp_field
        if not has_animated_webp_field:
            return

        file = getattr(instance, self.attname)

        if not file and not force:
            return

        animated_wep_field_filled = not(self.animated_webp_field and not getattr(instance, self.animated_webp_field))

        if animated_wep_field_filled and not force:
            return

        if file:
            animated_wep = file.animated_wep
        else:
            animated_wep = None
        if self.animated_webp_field:
            setattr(instance, self.animated_webp_field, animated_wep)

    def update_mp4_field(self, instance, force = False, *args, **kwargs):
        has_mp4_field = self.mp4_field
        if not has_mp4_field:
            return

        file = getattr(instance, self.attname)

        if not file and not force:
            return

        mp4_field_filled = not(self.mp4_field and not getattr(instance, self.mp4_field))

        if mp4_field_filled and not force:
            return

        if file:
            mp4 = file.mp4
        else:
            mp4 = None
        if self.mp4_field:
            setattr(instance, self.mp4_field, mp4)

    def update_cover_fields(self, instance, force=False, *args, **kwargs):
        has_cover_fields = self.cover_start_second_filed or self.cover_duration_filed
        if not has_cover_fields:
            return

        file = getattr(instance, self.attname)

        if not file and not force:
            return

        cover_fields_filled = not (
            (self.cover_duration_filed and not getattr(instance, self.cover_duration_filed))
            or (self.cover_start_second_filed and not getattr(instance, self.cover_start_second_filed))
        )

        if cover_fields_filled and not  force:
            return

        if file:
            cover_duration = file.cover_duration
            cover_start_second = file.cover_start_second
        else:
            cover_duration = None
            cover_start_second = None

        if self.cover_start_second_filed:
            setattr(instance, self.cover_start_second_filed, cover_start_second)
        if self.cover_duration_filed:
            setattr(instance, self.cover_duration_filed, cover_duration)

    # def update_aac_field(self, instance, force=False, *args, **kwargs):
    #     has_aac_field = self.aac_field
    #     if not has_aac_field:
    #         return
    #
    #     file = getattr(instance, self.attname)
    #
    #     if not file and not force:
    #         return
    #
    #     aac_field_filled = not (self.aac_field and not getattr(instance, self.aac_field))
    #
    #     if aac_field_filled and not force:
    #         return
    #
    #     if file:
    #         aac = file.aac
    #     else:
    #         aac = None
    #     if self.mp4_field:
    #         setattr(instance, self.aac_field, aac)




    def formfield(self, **kwargs):
        defaults = { 'form_class' : VideoFormField }
        defaults.update(kwargs)
        return super(VideoField, self).formfield(**defaults)


# class VideoSpecField(VideoField):
#     attr_class = VideoSpecFieldFile
#     descriptor_class = VideoSpecFileDescriptor
#
#     def __init__(   self, verbose_name = None, name = None,
#                     source = None,
#                     format = VideokitConfig.VIDEOKIT_DEFAULT_FORMAT,
#                     storage = None,
#                     # video_cache_backend = None,
#                     **kwargs):
#         self.source = source
#         self.format = format
#         self.storage = storage or default_storage
#         # self.video_cache_backend = video_cache_backend or get_videokit_cache_backend()
#
#         kwargs.pop('blank', None)
#         kwargs.pop('null', None)
#
#         if not format in VideokitConfig.VIDEOKIT_SUPPORTED_FORMATS:
#             raise ValueError('Video format \'%s\' is not supported at this time by videokit.' % format)
#
#         super(VideoSpecField, self).__init__(verbose_name, name, blank = True, null = True, **kwargs)
#
#     def form_field(self, **kwargs):
#         return None
