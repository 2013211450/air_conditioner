#!/usr/bin/env python

import django

import socket
import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'air_conditioner.settings'
django.setup()
from django.contrib.auth.models import User
from app.models import Room, Server
from app.service import get_server_host

if __name__ == '__main__':
    print BASE_DIR
    '''
    print get_server_host()
    user = User.objects.filter(username='liuwei').first()
    if user:
        server = Server.objects.filter(user_id=user.id).first()
        if not server:
            server = Server.objects.create(user_id=user.id)
        else:
            print user.is_superuser
            print server.id
    else:
        print "ERROR"
    '''
    rooms = Room.objects.all()
    '''
    room = Room.objects.first()
    room.numbers = '111222'
    room.save()
    '''
    for room in rooms:
        print room.numbers
    # room = Room.objects.get(user_id=user.id)
    # server = Server.objects.first()
    # for i in range(8, 11):
    #     user = User.objects.create_user('test_0'+str(i), 'test@qq.com','123123')
    #    print user.id
    #    print user.username
    #    print room.host
