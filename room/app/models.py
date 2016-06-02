# encoding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Room(models.Model):

    user_id = models.IntegerField(null=True, default=1, unique=True, db_index=True)
    numbers = models.CharField(max_length=8, null=True, default=0, unique=True)
    speed = models.IntegerField(null=True, default=0)
    price = models.FloatField(max_length=8, null=True, default=1.0)
    total_cost = models.FloatField(max_length=8, null=True, default=0.0)
    power = models.FloatField(max_length=8, null=True, default=0.0)
    room_temperature = models.FloatField(max_length=8, null=True, default=20.0)
    setting_temperature = models.FloatField(max_length=8, null=True, default=20.0)
    host = models.CharField(max_length=32, null=True, default='127.0.0.1:8000', db_index=True)
    ip_address = models.CharField(max_length=32, null=True, default='')
    mode = models.IntegerField(null=True, default=0)
    link = models.IntegerField(null=True, default=0)
    service = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = 'room_info'

