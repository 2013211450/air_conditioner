# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators  import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from service import get_server_host
from datetime import datetime, timedelta
import json
import urllib2, urllib
from models import Server, Room
# Create your views here.
MODE = ['cold', 'wait', 'hot']

def server_init():
    rooms = Room.objects.all()
    for room in rooms:
        room.service = 0
        room.link = 0
        room.mode = 0
        room.save()

def update_room_info(rooms):
    for room in rooms:
        if not room.service:
            continue
        room.power += room.speed * 0.05
        room.total_cost = room.power * room.price
        room.save()

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
    server.host = host + ':' + port
    if not server.work:
        server_init()
    server.work = 1
    server.save()
    print server.host
    count = Room.objects.filter(host=server.host, link=1).count()
    page_count = (count + page_size - 1)/ page_size
    if page_count < 1:
        page_count = 1
    if offset > count:
        offset = count
    if offset + page_size > count:
        page_size = count - offset
    rooms = Room.objects.filter(host=server.host, link=1)[offset:(offset+page_size)]
    update_room_info(rooms)
    return render(request, 'center.html', {'rooms': rooms, 'page_num':page_num, 'page_count': page_count, 'user':user})

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
            print request.user.username
            server = Server.objects.filter(user_id=request.user.id).first()
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
        return JsonResponse({'type': 'query_mode', 'source': 'host', 'ack_nak': 'ACK', 'mode': MODE[room.mode]})



