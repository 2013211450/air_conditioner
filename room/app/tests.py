#!/usr/bin/env python

import django

import socket
import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
# sys.path.append('/home/liuwei/air_conditioner/room/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'air_conditioner.settings'
django.setup()

from django.contrib.auth.models import User
from app.models import Room
from app.service import get_server_host

if __name__ == '__main__':
    for i in range(1, 10):
        user = User.objects.filter(username='test'+str(i)).first()
        if not user:
            user = User.objects.create_user('test'+str(i), 'test@qq.com', '123123')
        room = Room.objects.filter(user_id=user.id).first()
        if room:
            print 'Exist'
            print room.id
            room.speed = 0
            room.mode = 0
            room.save()
        else:
            room = Room.objects.create(user_id=user.id, numbers='40'+str(i), room_temperature=27.9)
            print 'create' 
            print room.id
    # room = Room.objects.get(user_id=user.id)
    # server = Server.objects.first()
    # for i in range(8, 11):
    #     user = User.objects.create_user('test_0'+str(i), 'test@qq.com','123123')
    #    print user.id
    #    print user.username
    #    print room.host

