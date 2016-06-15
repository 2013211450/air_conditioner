# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators  import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from service import get_server_host
from datetime import datetime, timedelta, date
import json
import urllib2, urllib
from models import Server, Room, CostPerDay
# Create your views here.
MODE = ['cold', 'wait', 'hot']

MODE_DICT = {
        'cold': u'制冷',
        'wait': u'待机',
        'hot': u'制热',
        }

SPEED = ['standby', 'low', 'medium', 'high']

RESPEED = {
        'standby' : 0,
        'low': 1,
        'medium': 2,
        'high': 3,
        }

SPEED_DICT = {
        'standby': u'待机',
        'low': u'低速风',
        'medium': u'中速风',
        'high': u'高速风',
        }

POWER_PER_MIN = [0, 0.8, 1.0, 1.3]

def server_init():
    rooms = Room.objects.all()
    for room in rooms:
        room.service = 0
        room.link = 0
        room.save()

@login_required
def get_report(request):
    print request.GET
    room_id = request.GET.get('room_id', None)
    if not room_id:
        return HttpResponseRedirect('/')
    room_id = int(room_id)
    start_date = request.GET.get('start_date', None)
    if not start_date:
        start_date = date.today()
    end_date = request.GET.get('end_date', None)
    if not end_date:
        end_date = date.today()
    query = CostPerDay.objects.filter(room_id=room_id, create_time__gte=start_date, create_time__lte=end_date)
    data = query.all()
    if query.count() > 10:
        data = data[0:10]
    resp = {}
    resp['list'] = []
    resp['numbers'] = Room.objects.filter(id=room_id).first().numbers
    total_power = 0.0
    total_cost = 0.0
    for r in data:
        total_power += r.day_power
        total_cost += r.day_cost
        resp['list'].append({
            'date': str(r.create_time),
            'power': r.day_power,
            'cost': r.day_cost,
        })
    resp['total_cost'] = total_cost
    resp['total_power'] = total_power
    return render(request, 'report.html', resp)


def post_to_client(host, attr):
    host = host.strip()
    print 'client host:  ', host
    req = urllib2.Request(host + '/communication')
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
        else:
            print "--------post refused-------"
    except Exception, ex:
        print ex
    return resp


def query_room_temperature(host, numbers):
    data = {'type':'check_temperature', 'source':'host'}
    resp = post_to_client(host, data)
    ans = {}
    if resp['code'] == 0:
        ans['room_temperature'] = resp['data']['room_temperature']
        ans['setting_temperature'] = resp['data']['setting_temperature']
        ans['code'] = 0
    else:
        ans['code'] = -1
        print "query ERROR!=========="
    return ans


def update_cost(room_id, power, price):
    new_cost = CostPerDay.objects.filter(room_id=room_id, create_time=date.today()).first()
    if not new_cost:
        new_cost = CostPerDay.objects.create(room_id=room_id, create_time=date.today())
    new_cost.day_power += power
    new_cost.day_cost += power * price
    new_cost.save()

@login_required
def update_room_info(request):
    mode = Server.get_attr('mode')
    query = Room.objects.select_for_update().filter(host=Server.get_host(), link=1)
    for room in query.all():
        resp = query_room_temperature(room.ip_address, room.numbers)
        if not room.link:
            continue
        if resp['code'] == 0:
            room.setting_temperature = resp['setting_temperature']
            room.room_temperature = resp['room_temperature']
        else:
            room.link = 0
            room.service = 0
            print "break link!"
        room.save()
        if not room.service:
            continue
        if room.speed == 0:
            room.service = 0
        if (room.setting_temperature >= room.room_temperature + 0.1 and mode == 0) or (room.setting_temperature + 0.1 <= room.room_temperature and mode == 2):
            room.speed = 0
            room.service = 0
        if room.service == 0:
            resp = post_to_client(room.ip_address, {'type':'stop', 'source': 'host'})
        print 'numbers', room.numbers
        update_cost(room.id, POWER_PER_MIN[room.speed], room.price)
        room.power += POWER_PER_MIN[room.speed]
        room.total_cost = room.power * room.price
        room.save()
    service_count = query.filter(service=1).count()
    if service_count < 3:
        rooms = query.filter(service=0, speed__gt=0).all()
        for room in rooms:
            if (room.setting_temperature >= room.room_temperature + 0.1 and mode == 0) or (room.setting_temperature + 0.1 <= room.room_temperature and mode == 2):
                continue
            resp = post_to_client(room.ip_address, {'type':'send', 'source':'host'})
            if resp['code'] == 0:
                room.service = 1
                room.start_service_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                room.save()
            break

    return JsonResponse({'code': 0})


@login_required
def profile(request):
    host = get_server_host()
    port = request.get_port()
    user = request.user
    if not user.is_superuser:
        print "ERROR"
        return HttpResponseRedirect('/account/logout/')
    page_num = request.GET.get('page_num', 1)
    page_num = int(page_num)
    page_size = 6
    offset = page_size * (page_num - 1)
    server = Server.objects.filter(user_id=user.id).first()
    host = host + ':' + port
    server.host = host
    if not server.work:
        server_init()
    server.work = 1
    server.save()
    count = Room.objects.filter(host=server.host).count()
    page_count = (count + page_size - 1)/ page_size
    if page_count < 1:
        page_count = 1
    if offset > count:
        offset = count
    if offset + page_size > count:
        page_size = count - offset
    rooms = Room.objects.filter(host=server.host)[offset:(offset+page_size)]
    data = []
    for room in rooms:
        is_service = u'服务中'
        is_link = u'已连接'
        if not room.service:
            is_service = u'未服务'
        if not room.link:
            is_link = u'连接已断开'
        room_mode = MODE_DICT[MODE[Server.get_attr('mode')]]
        room_speed = SPEED_DICT[SPEED[room.speed]]
        data.append({
            'id': room.id,
            'is_link': is_link,
            'numbers':room.numbers,
            'ip_address': room.ip_address,
            'service': is_service,
            'mode': room_mode,
            'speed': room_speed,
            'power': CostPerDay.get_power(room.id, back=Server.get_report_days()),
            'room_temperature': room.room_temperature,
            'setting_temperature': room.setting_temperature,
            'total_cost': CostPerDay.get_cost(room.id, back=Server.get_report_days()),
            'rest_cost': room.total_cost,
            })
    return render(request, 'center.html', {'list': data, 'page_num':page_num, 'page_count':
        page_count, 'user':user, 'host': host, 'report': Server.get_report_name(), 'mode':
        MODE_DICT[MODE[server.mode]]})


def account_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        auth_user = User.objects.filter(username=username).first()
        if not auth_user or not auth_user.is_superuser:
            return JsonResponse({'code': -1, 'reason': '用户不存在'})
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            server = Server.objects.filter(user_id=request.user.id).first()
            today = date.today()
            if today.month > 3 and today.month < 10:
                server.mode = 0
            else:
                server.mode = 2
            if not server:
                auth.logout(request, user)
                return JsonResponse({'code': -1, 'reason': '用户不存在'})
            server.work = 1
            server.save()
            server_init()
            return JsonResponse({'code': 0, 'reason': '登录成功'})
        else:
            return JsonResponse({'code': -1, 'reason': '登录失败'})


@login_required
def account_logout(request):
    # import pdb
    # pdb.set_trace()
    user = request.user
    print user.username
    print "user_id: ", user.id
    if not user.is_superuser:
        auth.logout(request)
        return HttpResponseRedirect('/')
    server = Server.objects.filter(user_id=user.id).first()
    server.work = 0
    server.save()
    rooms = Room.objects.all()
    for room in rooms:
        room.link = 0
        room.save()

@login_required
def checkout(request):
    numbers = request.POST.get('numbers', '')
    room = Room.objects.filter(numbers=numbers).first()
    if not room:
        print 'numbers Error %s !' % numbers
    print 'checkout room.ip_address: ', room.ip_address
    room.service = 0
    room.link = 1
    room.speed = 0
    room.total_cost = 0
    room.power = 0
    room.save()
    resp = post_to_client(room.ip_address, {'type':'stop', 'source': 'host'})
    return  JsonResponse({'code':0, 'reason':u'退房成功'})

def startservice(numbers):
    query = Room.objects.select_for_update()
    count = query.count()
    if count > 3:
        return True
    else:
        room = query.filter(numbers=numbers).first()
        room.service = 1
        room.start_service_time = datetime.now()
        room.save()
        return True


@login_required
def change_center(request):
    attr = request.POST.get('type', '')
    if attr == 'report':
        Server.change_report()
        return JsonResponse({'code':0})
    elif attr == 'mode':
        Server.change_mode()
        return JsonResponse({'code':0})
    else:
        print 'ERROR PARAM:', attr

def get_rand_name():
    user = User.objects.order_by("-id").first()
    return 'test'+str(user.id+1)

def communication(request):
    import pdb
    # pdb.set_trace()
    print "start=====com"
    if request.method != 'POST':
        resp = JsonResponse({'type': 'login', 'source': 'host', 'ack_nak': 'NAK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    source = request.POST.get('source', '')
    op = request.POST.get('type', 'login')
    room = Room.objects.select_for_update().filter(numbers=source).first()
    print "operator======, ", op
    if op == 'login':
        if not room:
            user = User.objects.create(username=get_rand_name(), password='xxxx')
            room = Room.objects.create(user_id=user.id, numbers=source)
        ip_port = request.POST.get('ip_port', None)
        print "ip___port:_______  ", ip_port
        room.ip_address = ip_port
        room.host = Server.get_host()
        room.link = 1
        room.save()
        print "========================="
        resp = JsonResponse({'type':'login', 'source':'host', 'ack_nak': 'ACK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    if not room:
        resp = JsonResponse({'type': op, 'source': 'host', 'ack_nak': 'NAK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    if op == 'logout':
        room.link = 0
        room.save()
        resp = JsonResponse({'type':'logout', 'source':'host', 'ack_nak': 'ACK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    elif op == 'require':
        speed = request.POST.get('speed', 'low')
        room.speed = RESPEED[speed]
        room.save()
        resp = JsonResponse({'type':'require', 'source':'host', 'ack_nak': 'ACK'})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    elif op == 'query_cost':
        resp = JsonResponse({'type': 'query_cost', 'source': 'host', 'ack_nak': 'ACK', 'power_consumption': room.power,
                             'price': room.price, 'total_cost': room.total_cost})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    elif op == 'query_mode':
        resp = JsonResponse({'type': 'query_mode', 'source': 'host', 'ack_nak': 'ACK', 'mode': MODE[Server.get_attr('mode')]})
        resp['Access-Control-Allow-Origin'] = '*'
        return resp


