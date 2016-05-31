from __future__ import unicode_literals
import re, socket
from models import Room, Server
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
    ipname = socket.gethostname()
    ipList = socket.gethostbyname_ex(ipname)
    print ipList
    return get_host(ipList)


def push_queue(room_id):
    query = Room.objects.select_for_update()
    count = query.filter(Room.service=0).count()
    if count > MAX_SERVICE_NUM:
        return False
    room = query.filter(Room.id=room_id).first()
    room.service = 1
    room.save()
    return True
