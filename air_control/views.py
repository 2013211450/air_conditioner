# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators  import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from service import get_server_host
import json
from models import Server, Room
# Create your views here.

@login_required
def profile(request):
    print 'count', Server.objects.count()
    if request.user.is_superuser:
        page_num = request.GET.get('page_num', 1)
        page_num = int(page_num)
        page_size = 6
        offset = page_size * (page_num - 1)
        server = Server.objects.get(user_id=request.user.id)
        host = get_server_host()
        port = request.get_port()
        print 'host:', host
        server.host = host + ':' + port
        server.save()
        print server.host
        count = Room.objects.filter(host=server.host).count()
        page_count = (count + page_size - 1)/ page_size
        if offset > count:
            offset = count
        if offset + page_size > count:
            page_size = count - offset
        rooms = Room.objects.filter(host=server.host)[offset:(offset+page_size)]
        return render(request, 'center.html', {'rooms': rooms, 'page_num':page_num, 'page_count': page_count})
    else:
        html = 'index.html'
    return render(request, html)

# @login_required
def control_settings(request):
    return render(request, 'settings.html')

@login_required
def admin_settings(request):
    return render(request, 'admin_settings.html')

@login_required
def update_password(request):
    pass


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
            return JsonResponse({'code': 0, 'reason': '登录成功'})
        else:
            return JsonResponse({'code': -1, 'reason': '登录失败'})

@login_required
def account_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
