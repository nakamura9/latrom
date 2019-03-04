import os
DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
# set to the ip address of the server
ALLOWED_HOSTS = ["localhost", '127.0.0.1']

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

WKHTMLTOPDF_CMD = os.path.abspath(os.path.join(BASE_DIR, '..', 'bin', 'wkhtmltopdf', 'bin'))
