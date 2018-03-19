# -*- coding: utf-8 -*-
# @Time    : 3/19/18 10:35 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : forms.py
# @Software: PyCharm

from django import forms
from videokit.forms import VideoField

class MediaItemUploadForm(forms.Form):
    video = VideoField()
