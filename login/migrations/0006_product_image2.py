# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-25 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_auto_20190124_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='photos', verbose_name='\u56fe\u7247'),
        ),
    ]
