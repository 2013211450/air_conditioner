#!/usr/bin/env python

import django

import socket
import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'air_conditioner.settings'
django.setup()
from django.contrib.auth.models import User
from app.models import Room, Server, CostPerDay
from app.service import get_server_host
from datetime import datetime, date

if __name__ == '__main__':
    print BASE_DIR
    rooms = Room.objects.all()
    for room in rooms:
        room.speed = 0
        room.save()
    '''
    room = Room.objects.first()
    room.numbers = '111222'
    room.save()
    '''
    # room = Room.objects.get(user_id=user.id)
    # server = Server.objects.first()
    # for i in range(8, 11):
    #     user = User.objects.create_user('test_0'+str(i), 'test@qq.com','123123')
    #    print user.id
    #    print user.username
    #    print room.host
