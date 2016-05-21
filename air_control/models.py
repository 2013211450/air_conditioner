# encoding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Room(models.Model):

    user_id = models.IntegerField(null=True, default=1, unique=True, db_index=True)
    numbers = models.CharField(max_length=8, null=True, default=0, unique=True)
    speed = models.IntegerField(null=True, default=1)
    price = models.FloatField(max_length=8, null=True, default=0.0)
    total_cost = models.FloatField(max_length=8, null=True, default=0.0)
    room_temperature = models.FloatField(max_length=8, null=True, default=20.0)
    setting_temperature = models.FloatField(max_length=8, null=True, default=20.0)
    host = models.CharField(max_length=32, null=True, default='127.0.0.1:8000', db_index=True)
    ip_address = models.CharField(max_length=32, null=True, default='')
    mode = models.IntegerField(null=True, default=0)
    link = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = 'room_info'

class Server(models.Model):

    user_id = models.IntegerField(null=True, default=1, unique=True, db_index=True)
    host = models.CharField(max_length=32, null=True, default='127.0.0.1:8000')

    class Meta:
        db_table = 'server_info'

class Profile(models.Model):

    '''User扩展信息'''
    user = models.OneToOneField(User)
    now_identity= models.CharField(max_length=32, null=True, default='')
    def __unicode__(self):
        return self.user.username

    class Meta:
        db_table = 'account_profile'

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


