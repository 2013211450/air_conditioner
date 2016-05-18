import django
import sys, os
sys.path.append('/Users/liuwei/PycharmProjects/air_conditioner/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'air_conditioner.settings'
django.setup()
from django.contrib.auth.models import User

if __name__ == '__main__':
    # user = User.objects.create_user('xixihaha', 'bupt2013211450@gmail.com', '248035')
    user = User.objects.filter(username='xixihaha').first()
    pro = user.profile
    print pro.ip_address

