import os
import json

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
    
ALLOWED_HOSTS = ["*"]


def get_current_database():
    global BASE_DIR
    with open(os.path.join(BASE_DIR, 'database', 'config.json'), 'r') as conf:
        config = json.load(conf)
        print(f"Current Database: {config['current']}")
        return config['current']


#TODO update with the new database util
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'database' ,get_current_database()),
    },
    
}

#DATABASE_ROUTERS = ['messaging.db.router.MessagingRouter']

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '/',
        'STATS_FILE': os.path.join(BASE_DIR, 'assets', 'webpack-stats.json'),
    }
}

def get_backup_location():
     global BASE_DIR
     with open(os.path.join(BASE_DIR, 'database', 'config.json'), 'r') as conf:
        config = json.load(conf)
        return config.get('backup_dir', "")
        

DBBACKUP_STORAGE_OPTIONS = {'location': get_backup_location()}
