# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators  import login_required
from django.contrib import auth
import json
# Create your views here.

@login_required
def profile(request):
    html = 'index.html'
    return render(request, html)

@login_required
def control_settings(request):
    return render(request, 'settings.html')

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
    return JsonResponse({'code':0, 'reason':'注销成功!'})
