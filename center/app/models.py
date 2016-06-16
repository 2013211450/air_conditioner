# encoding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from datetime import datetime, timedelta, date

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
    link = models.IntegerField(null=True, default=0)
    service = models.IntegerField(null=True, default=0)
    start_service_time = models.DateTimeField(null=True, default=None)

    class Meta:
        db_table = 'room_info'


class Server(models.Model):

    user_id = models.IntegerField(null=True, default=1, unique=True, db_index=True)
    host = models.CharField(max_length=32, null=True, default='127.0.0.1:8000')
    work = models.IntegerField(null=True, default=0)
    mode = models.IntegerField(null=True, default=0)
    report = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = 'server_info'

    @classmethod
    def get_attr(cls, attr):
        server = cls.objects.first()
        return getattr(server, attr, None)

    @classmethod
    def get_host(cls):
        return cls.objects.first().host

    @classmethod
    def change_mode(cls):
        server = cls.objects.first()
        server.mode = (server.mode + 1) % 3
        server.save()

    @classmethod
    def change_report(cls):
        server = cls.objects.first()
        server.report = (server.report + 1) % 4
        server.save()

    @classmethod
    def get_report_name(cls):
        server = cls.objects.first()
        name = [u'日消费', u'周消费', u'月消费', u'访客总消费']
        return name[server.report]

    @classmethod
    def get_report_days(cls):
        server = cls.objects.first()
        print server.report
        days = [1, 7, 31, 365]
        return days[server.report]


class CostPerDay(models.Model):

    room_id = models.IntegerField(null=True, default=1, db_index=True)
    day_power = models.FloatField(max_length=8, null=True, default=0.0)
    day_cost = models.FloatField(max_length=8, null=True, default=0.0)
    create_time = models.DateField(null=True, default=None, db_index=True)

    class Meta:
        db_table = 'cost_per_day'

    @classmethod
    def get_cost(cls, roomid=1, back=1):
        today = date.today()
        last_day = today - timedelta(days=back)
        res = cls.objects.filter(room_id=roomid, create_time__range=[last_day.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d')]).all()
        ans = 0.0
        for r in res:
            ans += r.day_cost
        return ans

    @classmethod
    def get_power(cls, roomid=1, back=1):
        today = date.today()
        last_day = today - timedelta(days=back)
        res = cls.objects.filter(room_id=roomid, create_time__range=[last_day, today]).all()
        ans = 0.0
        for r in res:
            ans += r.day_power
        return ans

class RoomRequest(models.Model):

    room_id = models.IntegerField(null=True, default=1, db_index=True)
    start_time = models.DateTimeField(null=True, default=None)
    end_time = models.DateTimeField(null=True, default=None)
    start_temperature = models.FloatField(max_length=8, null=True, default=20.0)
    end_temperature = models.FloatField(max_length=8, null=True, default=20.0)
    power = models.FloatField(max_length=8, null=True, default=0.0)
    cost = models.FloatField(max_length=8, null=True, default=0.0)
    speed = models.IntegerField(null=True, default=0)

