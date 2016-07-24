import os

try:
    from secrets import *
except:
    ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID')
    SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')
