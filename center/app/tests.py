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
from app.views import update_room_info
import time

if __name__ == '__main__':
    print BASE_DIR
    while True:
        update_room_info()
        time.sleep(2)
