# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators  import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from service import get_server_host
import json
import urllib2, urllib
from models import Room
# Create your views here.
MODE = [u'制冷', u'待机', u'制热']
MODE_DICT = {'hot':2, 'cold':0, 'wait':1}
SPEED = [u'待机', u'低速风', u'中速风', u'高速风']
SPEED_DICT = ['standby', 'low', 'medium', 'hight']
# SPEED_DICT = {'low':1, 'medium':2, 'hight':3, 'standby':0}

@login_required
def profile(request):
    host = get_server_host()
    port = request.get_port()
    user = request.user
    room = Room.objects.filter(user_id=user.id).first()
    if not room.setting_temperature:
        room.setting_temperature = 20.0
    print host
    print port
    room.ip_address = host + ':' + port
    if room.link == 1:
        room.mode = query_server_mode(room.host, room.numbers)
    room.save()
    print room.ip_address
    return render(request, 'index.html', {'user': request.user, 'room':room, 'speed':SPEED[room.speed], 'mode': MODE[room.mode]})

@login_required
def control_settings(request):
    import pdb
    if request.method == 'POST':
        host = request.POST.get('host', '127.0.0.1:8000')
        room = Room.objects.get(user_id=request.user.id)
        room.host = host
        room.ip_address = get_server_host() + ':' + request.get_port()
        resp = connect_to_server(room.numbers, room.host, room.ip_address)
        if resp['code'] == 0:
            room.link = 1
            room.save()
        return JsonResponse(resp)

@login_required
def operator(request):
    if request.method == 'POST':
        room = Room.objects.filter(user_id=request.user.id).first()
        print "request info: ", request.POST
        if request.POST.has_key('speed'):
            speed = int(request.POST['speed'])
            speed = (speed + 1) % 4
            resp = post_to_server(room.host, {'type':'require', 'source':room.numbers, 'speed':SPEED_DICT[speed]})
            if resp['code'] == 0:
                room.speed = speed
                room.save()
            resp = {'code' : 0, 'msg':'success'}
            resp['speed'] = SPEED[room.speed] 
        if request.POST.has_key('temperature'):
            resp = {'code' : 0, 'msg':'success'}
            temperature = float(request.POST['temperature'])
            room.mode = query_server_mode(room.host, room.numbers)
            if room.mode == 0:
                if room.setting_temperature < 25.0 or temperature < 0:
                    room.setting_temperature += temperature
                elif room.setting_temperature > 18.0 and temperature > 0:
                    room.setting_temperature += temperature
            elif room.mode == 2:
                if room.setting_temperature < 30.0 or temperature < 0:
                    room.setting_temperature += temperature
                elif room.setting_temperature > 25.0 and temperature > 0:
                    room.setting_temperature += temperature
            room.setting_temperature += temperature
            resp['setting_temperature'] = room.setting_temperature
            room.save()
    return JsonResponse(resp)

def post_to_server(host, data):
    req = urllib2.Request('http://' + host + '/communication/')
    data = urllib.urlencode(data)
    resp = {'code':-1, 'reason':u'发送失败'}
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    try:
        response = opener.open(req, data, timeout=2)
        content = response.read()
        if isinstance(content, str):
            content = json.loads(content)
        if content['ack_nak'] == 'ACK':
            resp = {'code': 0, 'data': content}
    except Exception, ex:
        print ex
    return resp

def query_server_mode(host, numbers):
    data = {'type':'query_mode', 'source':numbers}
    resp = post_to_server(host, data)
    if resp['code'] == 0:
        data = resp['data']
        return MODE_DICT[data['mode']]
    return 0

def connect_to_server(numbers, host, ip_port):
    # pdb.set_trace()
    data = {'type': 'login',  'source': numbers, 'ip_port': ip_port}
    resp = post_to_server(host, data)
    return resp

def account_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        flag = False
        if user and user.is_active:
            room = Room.objects.filter(user_id=user.id).first()
            if room:
                host = get_server_host()
                port = request.get_port()
                host = host + ':' + str(port)
                room.ip_address = host
                room.link = 0
                room.save()
            auth.login(request, user)
            return JsonResponse({'code': 0, 'reason': '登录成功'})
        else:
            return JsonResponse({'code': -1, 'reason': '登录失败'})

@login_required
def account_logout(request):
    # import pdb
    # pdb.set_trace()
    user = request.user
    room = Room.objects.filter(user_id=user.id).first()
    if room:
        room.service = 0
        room.link = 0
        room.save()
        post_to_server(room.host, {'type':'logout', 'source':room.numbers})
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def get_info(request):
    user = request.user
    attr = request.POST.get('attr', '')
    room = Room.objects.get(user_id=user.id)
    resp = {}
    try:
        attr_list = attr.split(',')
        for r in attr_list:
            resp[r] = getattr(room, r, '')
    except Exception, ex:
        print "get_info: ", ex
        print attr
    if room.service == 1:
        room.room_temperature += room.speed * 0.1 * (room.mode - 1) 
        room.save()
    return JsonResponse(resp)

def communication(request):
    import pdb
    # pdb.set_trace()
    if request.method != 'POST':
        return JsonResponse({'type': 'login', 'source': 'host', 'ack_nak': 'NAK'})
    source = request.POST.get('source', '')
    room = Room.objects.filter(host=request.get_host()).first()
    if not room:
        return JsonResponse({'type': op, 'source': 'host', 'ack_nak': 'NAK'})
    op = request.POST.get('type', 'login')
    if op == 'send':
        ip_port = request.POST.get('ip_port', None)
        room.service = 1
        room.save()
        return JsonResponse({'type':'send', 'source': room.numbers, 'ack_nak': 'ACK'})
    elif op == 'stop':
        room.service = 0
        room.save()
        return JsonResponse({'type':'stop', 'source': room.numbers, 'ack_nak': 'ACK'})
    elif op == 'check_temperature':
        return JsonResponse({'type': 'check_temperature', 'source': room.numbers, 'ack_nak': 'ACK', 'room_temperature': room.room_temperature,
                'setting_temperature': room.setting_temperature})

