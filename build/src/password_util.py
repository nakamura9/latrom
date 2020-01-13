import sys 
import os 
from django.contrib.auth.hashers import make_password

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'server.latrom.settings')

with open('hashed_password.txt', 'w') as fil:
    fil.write(make_password(sys.argv[1]))
