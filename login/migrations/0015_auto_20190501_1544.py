# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-05-01 07:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0014_auto_20190430_1333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outitem',
            name='dhlshippingfeeInput',
        ),
        migrations.RemoveField(
            model_name='outitem',
            name='siteinput',
        ),
        migrations.RemoveField(
            model_name='outstock',
            name='tag_done',
        ),
        migrations.RemoveField(
            model_name='outstock',
            name='tag_pre',
        ),
        migrations.AddField(
            model_name='outitem',
            name='freightfee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='\u8fd0\u8d39'),
        ),
    ]