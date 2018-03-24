# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-03-19 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_locationstockreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponcode',
            name='emails',
            field=models.CharField(blank=True, help_text='comma separated list of emails to restrict coupon access to. Leave this blank otherwise.', max_length=1024),
        ),
    ]