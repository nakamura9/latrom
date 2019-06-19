import os
import socket

DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
# set to the ip address of the server
def get_host_names():
    """Only works on windows"""
    return socket.gethostbyname_ex(socket.gethostname())[2]


ALLOWED_HOSTS = ["localhost", '127.0.0.1'] + get_host_names()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'database', 'db.sqlite3'),
    }
}


WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

#WKHTMLTOPDF_CMD = os.path.abspath(os.path.join(BASE_DIR, '..', 'bin', 'wkhtmltopdf', 'bin'))

WKHTMLTOPDF_DEBUG = True

DBBACKUP_STORAGE_OPTIONS = {
    'location': os.path.join(BASE_DIR, '..', 'database')
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django.db.backends.schema': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}