import sys 
import os 
from django.contrib.auth.hashers import make_password

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'server.latrom.settings')

fil = open('hashed_password.txt', 'w')
fil.write(make_password(sys.argv[1]))
fil.close()
