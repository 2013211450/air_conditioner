import django
import socket
import sys, os
sys.path.append('/Users/liuwei/PycharmProjects/air_conditioner/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'air_conditioner.settings'
django.setup()
from django.contrib.auth.models import User
from air_control.models import Room, Server
from air_control.service import get_server_host
if __name__ == '__main__':
    # user = User.objects.create_user('xixihaha', 'bupt2013211450@gmail.com', '248035')
    server = Server.objects.first()
    for i in range(8, 11):
        user = User.objects.create_user('test_0'+str(i), 'test@qq.com','123123')
        room = Room.objects.create(user_id=user.id, numbers='30'+str(i), host=server.host, room_temperature=27.9)
        print user.id
        print user.username
        print room.host

