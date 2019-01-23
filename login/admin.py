# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import models
from django.contrib import admin

# Register your models here.

admin.site.register(models.User)
admin.site.site_url = '/index/'#修改admin中的viewsite的默认值