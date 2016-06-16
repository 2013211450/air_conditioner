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
MODE = [u'制冷', u'未链接', u'制热']
MODE_DICT = {'hot':2, 'cold':0, 'wait':1}
SPEED = [u'待机', u'低速风', u'中速风', u'高速风']
SPEED_DICT = ['standby', 'low', 'medium', 'high']
# SPEED_DICT = {'low':1, 'medium':2, 'hight':3, 'standby':0}

@login_required
def profile(request):
    print request.META['HTTP_ACCEPT']
    host = get_server_host()
    port = request.get_port()
    user = request.user
    room = Room.objects.filter(user_id=user.id).first()
    if not room.setting_temperature:
        room.setting_temperature = 20.0
    room.ip_address = host + ':' + port
    mode = 1
    if room.link == 1:
        mode = query_server_mode(room.host, room.numbers)
        if mode == -1:
            room.service = 0
            room.speed = 0
        update_cost(room)
    room.save()
    count = Room.objects.filter(link=1).count()
    if count > 0:
        rooms = Room.objects.filter(link=1).all()
        for r in rooms:
            if r == room:
                print r.numbers
                continue
            print "break ", r.numbers
            r.link=0
            r.speed=0
            r.save()

    print 'room_numbers: ', room.numbers
    print 'is_link: ', room.link
    return render(request, 'index.html', {'user': request.user, 'room':room, 'speed':SPEED[room.speed], 'mode': MODE[mode]})

@login_required
def control_settings(request):
    import pdb
    if request.method == 'POST':
        host = request.POST.get('host', '127.0.0.1:8000')
        room = Room.objects.get(user_id=request.user.id)
        print 'link host: ', host
        room.host = host
        room.ip_address = get_server_host() + ':' + request.get_port()
        print room.ip_address
        resp = connect_to_server(room.numbers, room.host, 'http://'+room.ip_address)
        if resp['code'] == 0:
            print "======link sus====="
            print room.numbers
            room.link = 1
            room.save()
        return JsonResponse(resp)

@login_required
def operator(request):
    if request.method == 'POST':
        room = Room.objects.filter(user_id=request.user.id).first()
        print "request info: ", request.POST
        if request.POST.has_key('speed'):
            speed = (room.speed + 1) % 4
            resp = post_to_server(room.host, {'type':'require', 'source':room.numbers, 'speed':SPEED_DICT[speed]})
            room.speed = speed
            if resp['code'] != 0:
                print resp['code']
            room.save()
            resp = {'code' : 0, 'msg':'success'}
            resp['speed_mode'] = SPEED[room.speed] 
        if request.POST.has_key('temperature'):
            resp = {'code' : 0, 'msg':'success'}
            temperature = float(request.POST['temperature'])
            mode = query_server_mode(room.host, room.numbers)
            '''
            if room.setting_temperature > room.room_temperature + 0.1:
                room.mode = 2
            elif room.room_temperature > room.setting_temperature + 0.1:
                room.mode = 0
            '''
            if mode == 0:
                if room.setting_temperature < 25.1 and temperature > 0:
                    room.setting_temperature += temperature
                elif room.setting_temperature > 17.9 and temperature < 0:
                    room.setting_temperature += temperature
            elif mode == 2:
                if (temperature > 0 and room.setting_temperature < 30.1) or (temperature < 0 and room.setting_temperature > 24.9):
                    room.setting_temperature += temperature
            resp['setting_temperature'] = room.setting_temperature
            room.save()
    return JsonResponse(resp)

def post_to_server(host, attr):
    req = urllib2.Request('http://' + host + '/communication')
    data = urllib.urlencode(attr)
    resp = {'code':-1, 'reason':u'发送失败'}
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    try:
        response = opener.open(req, data, timeout=2)
        content = response.read()
        if isinstance(content, str):
            content = json.loads(content)
        if content['ack_nak'] == 'ACK':
            resp = {'code': 0, 'data': content}
        if attr['type'] == 'login':
            print "=================="
            print "numbers:  ", attr['source']
            print content
    except Exception, ex:
        print ex
    return resp

def query_server_mode(host, numbers):
    data = {'type':'query_mode', 'source':numbers}
    resp = post_to_server(host, data)
    if resp['code'] == 0:
        data = resp['data']
        return MODE_DICT[data['mode']]
    else:
        print resp
    return -1

def update_cost(room):
    res = post_to_server(room.host, {'source': room.numbers, 'type':'query_cost'})
    if res['code'] == 0:
        data = res['data']
        room.power = data['power_consumption']
        room.price = data['price']
        room.total_cost = data['total_cost']

def connect_to_server(numbers, host, ip_port):
    # pdb.set_trace()
    data = {'type': 'login',  'source': numbers, 'ip_port': ip_port}
    resp = post_to_server(host, data)
    if resp['code'] == 0:
        resp['reason'] = u'链接成功'
    else:
        resp['reason'] = u'链接失败'
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
                room.speed = 0
                room.save()
            auth.login(request, user)
            return JsonResponse({'code': 0, 'reason': '登录成功'})
        else:
            return JsonResponse({'code': -1, 'reason': '登录失败'})
    else:
        print request.method
        print "=======method ERROR!===="
        return JsonResponse({'code': -1, 'reason': '登录失败'})


@login_required
def account_logout(request):
    # import pdb
    # pdb.set_trace()
    user = request.user
    room = Room.objects.filter(user_id=user.id).first()
    if room and room.link:
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
    res = {}
    try:
        attr_list = attr.split(',')
        for r in attr_list:
            res[r] = getattr(room, r, '')
        if res.has_key('speed'):
            res['speed'] = SPEED[int(res['speed'])]
    except Exception, ex:
        print "get_info: ", ex
        print attr
    if room.service == 1:
        mode = query_server_mode(room.host, room.numbers)
        if mode == -1:
            # room.link = 0
            room.service = 0
            room.speed = 0
            room.save()
            return JsonResponse(res)
        room.room_temperature += room.speed * 0.5 * (mode - 1)
        room.save()
        if (room.room_temperature >= room.setting_temperature + 0.1 and mode == 2) or \
                (room.room_temperature <= room.setting_temperature - 0.1 and mode == 0):
            room.speed = 0
            room.service = 0
            resp = post_to_server(room.host, {'type':'require', 'source':room.numbers, 'speed':SPEED_DICT[room.speed]})
            # if resp['code'] == 0:
            room.save()
    return JsonResponse(res)


def communication(request):
    import pdb
    # pdb.set_trace()
    if request.method != 'POST':
        resp =  JsonResponse({'type': 'login', 'source': 'host', 'ack_nak': 'NAK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    source = request.POST.get('source', '')
    room = Room.objects.filter(link=1).first()
    print "=============numbers======"
    print "numbers: ", room.numbers
    op = request.POST.get('type', 'login')
    print "=====request room========", op
    print request.get_host()
    if not room:
        resp = JsonResponse({'type': request.POST.get('type', ''), 'source': 'host', 'ack_nak': 'NAK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    if op == 'send':
        ip_port = request.POST.get('ip_port', None)
        room.service = 1
        room.save()
        resp = JsonResponse({'type':'send', 'source': room.numbers, 'ack_nak': 'ACK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    elif op == 'stop':
        room.service = 0
        room.speed = 0
        room.save()
        resp = JsonResponse({'type':'stop', 'source': room.numbers, 'ack_nak': 'ACK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    elif op == 'check_temperature':
        resp = JsonResponse({'type': 'check_temperature', 'source': room.numbers, 'ack_nak': 'ACK',
                'room_temperature': room.room_temperature, 
                'setting_temperature': room.setting_temperature})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        print op
