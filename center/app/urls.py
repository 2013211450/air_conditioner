
from views import *

from django.conf.urls import patterns, url

urlpatterns =  patterns('',
    url(r'^$', profile, name='profile'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^account/login/$', account_login, name='account_login'),
    url(r'^account/logout/$', account_logout, name='account_logout'),
    url(r'^change/$', change_mode, name='change_mode'),
    url(r'^communication/$', communication, name='communication'),

)
