
from views import *

from django.conf.urls import patterns, url

urlpatterns =  patterns('',
    url(r'^$', profile, name='profile'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^settings/$', control_settings, name='control_settings'),
    url(r'^operator/$', operator, name="operator"),
    url(r'^account/login/$', account_login, name='account_login'),
    url(r'^account/logout/$', account_logout, name='account_logout'),
)
