# encoding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Profile(models.Model):

    '''User扩展信息'''
    user = models.OneToOneField(User)
    ip_address = models.CharField(max_length=32, null=True, default='')
    remote_address = models.CharField(max_length=32, null=True, default='')
    now_identity= models.CharField(max_length=32, null=True, default='')

    def __unicode__(self):
        return self.user.username

    class Meta:
        db_table = 'account_profile'

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


