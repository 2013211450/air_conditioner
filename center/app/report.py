#!/usr/bin/env python
#encoding: utf-8

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
from datetime import datetime, date
import xlwt

def get_report(back=1, report_name=u'日报表'):
    pass

if __name__ == '__main__':
    today = date.today()
    get_report(1, u'日报表')
    if today.weekday() == 0:
        get_report(7, u'日报表')
    if today.day == 1:
        get_report(30, u'月报表')

