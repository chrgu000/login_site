# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-24 07:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_auto_20190324_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttemp',
            name='image',
            field=models.ImageField(blank=True, default='photos/americanfootball_NSqvub1.jpg ', null=True, upload_to='photos', verbose_name='\u56fe\u7247'),
        ),
    ]