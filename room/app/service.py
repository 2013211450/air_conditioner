from __future__ import unicode_literals
import re, socket
import netifaces
from models import Room
iprule = '[0-9]{2}\.([0-9]{1,3}\.){2}[0-9]{1,3}'
rule = re.compile(iprule)

MAX_SERVICE_NUM = 3

def get_host(ipList):
    if isinstance(ipList, str):
        group = rule.match(ipList)
        if group:
            return group.group(0)
        else:
            return None
    for ip in ipList:
        ipresp = get_host(ip)
        if ipresp:
            return ipresp
    return None


def get_server_host():
    for i in netifaces.interfaces(): 
        info = netifaces.ifaddresses(i) 
        if netifaces.AF_INET not in info:
            continue 
        ip = info[netifaces.AF_INET][0]['addr']
        print '=====', ip
        group = rule.match(ip.strip())
        if group:
            return group.group(0)
    return None

def push_queue(room_id):
    query = Room.objects.select_for_update()
    count = query.filter(service=0).count()
    if count > MAX_SERVICE_NUM:
        return False
    room = query.filter(id=room_id).first()
    room.service = 1
    room.save()
    return True
