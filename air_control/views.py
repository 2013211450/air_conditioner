# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators  import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from service import get_server_host
import json
import urllib2, urllib
from models import Server, Room
# Create your views here.

def server_init():
    rooms = Room.objects.all()
    for room in rooms:
        room.service = 0
        room.save()

@login_required
def profile(request):
    print 'count', Server.objects.count()
    host = get_server_host()
    port = request.get_port()
    user = request.user
    if user.is_superuser:
        page_num = request.GET.get('page_num', 1)
        page_num = int(page_num)
        page_size = 6
        offset = page_size * (page_num - 1)
        server = Server.objects.get(user_id=user.id)
        server.host = host + ':' + port
        if not server.work:
            server_init()
        server.work = 1
        server.save()
        print server.host
        count = Room.objects.filter(host=server.host, link=1).count()
        page_count = (count + page_size - 1)/ page_size
        if offset > count:
            offset = count
        if offset + page_size > count:
            page_size = count - offset
        rooms = Room.objects.filter(host=server.host, link=1)[offset:(offset+page_size)]
        return render(request, 'center.html', {'rooms': rooms, 'page_num':page_num, 'page_count': page_count, 'user':user})
    else:
        room = Room.objects.get(user_id=user.id)
        print host
        print port
        room.ip_address = host + ':' + port
        print room.ip_address
        return render(request, 'index.html', {'user': request.user, 'room':room})

@login_required
def control_settings(request):
    import pdb
    if request.method == 'POST':
        host = request.POST.get('host', '127.0.0.1:8000')
        room = Room.objects.get(user_id=request.user.id)
        room.host = host
        host = get_server_host() + ':' + request.get_port()
        room.ip_address = host
        room.save()
        req = urllib2.Request('http://' + room.host + '/communication/')
        # pdb.set_trace()
        data = {'type': 'login',  'source': room.numbers, 'ip_port': room.ip_address}
        data = urllib.urlencode(data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, data)
        content = response.read()
        if isinstance(content, str):
            content = json.loads(content)
        if content['ack_nak'] == 'ACK':
            resp = {'code': 0, 'reason': '链接主机成功'}
        else:
            resp = {'code': -1, 'reason': '链接主机失败'}
        return JsonResponse(resp)

@login_required
def admin_settings(request):
    return render(request, 'admin_settings.html')



@login_required
def operator(request):
    if request.method == 'POST':
        print "request info: ", request.POST
        if request.POST.has_key('temperature'):
            print request.POST['temperature']
    resp = {'code' : 0, 'msg':'success'}
    return JsonResponse(resp)

def account_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if request.user.is_superuser:
                Room.objects.filter(host=request.user.host).update(link=0)
            return JsonResponse({'code': 0, 'reason': '登录成功'})
        else:
            return JsonResponse({'code': -1, 'reason': '登录失败'})

@login_required
def account_logout(request):
    # import pdb
    # pdb.set_trace()
    user = request.user
    if user.is_superuser:
        server = Server.objects.get(user_id=user.id)
        server.work = 0
        server.save()
    else:
        room = Room.objects.get(user_id=user.id)
        room.service = 0
        room.link = 0
        room.save()
    auth.logout(request)
    return HttpResponseRedirect('/')

def startservice(address):
    query = Room.objects.select_for_update()
    count = query.count()
    if count > 3:
        return
    else:
        room = query.filter(numbers=address).first()
        room.service = 1
        room.save()
        return

def communication(request):
    import pdb
    # pdb.set_trace()
    if request.method != 'POST':
        return JsonResponse({'type': 'login', 'source': 'host', 'ack_nak': 'NAK'})
    source = request.POST.get('source', '')
    room = Room.objects.get(numbers=source)
    op = request.POST.get('type', 'login')
    if not room:
        return JsonResponse({'type': op, 'source': 'host', 'ack_nak': 'NAK'})
    if op == 'login':
        ip_port = request.POST.get('ip_port', None)
        room.ip_address = ip_port
        room.link = 1
        room.save()
        startservice(source)
        return JsonResponse({'type':'login', 'source':'host', 'ack_nak': 'ACK'})
    elif op == 'logout':
        room.link = 0
        room.save()
        return JsonResponse({'type':'logout', 'source':'host', 'ack_nak': 'ACK'})
    elif op == 'require':
        speed = request.POST.get('speed', 'low')
        if room.speed == speed:
            return JsonResponse({'type':'require', 'source':'host', 'ack_nak': 'ACK'})
        else:
            pass
    elif op == 'query_cost':
        return JsonResponse({'type': 'query_cost', 'source': 'host', 'ack_nak': 'ACK', 'power_consumption': room.power,
                             'price': room.price, 'total_cost': room.total_cost})
    elif op == 'query_mode':
        return JsonResponse({'type': 'query_mode', 'source': 'host', 'ack_nak': 'ACK', 'mode': room.mode})




