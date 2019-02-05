import os

from latrom.settings import USER_APPS
import shutil

for app in USER_APPS:
    print(app)
    path = os.path.join(app, 'migrations')
    shutil.rmtree(path)
    os.mkdir(path)
    filename = os.path.join(path, '__init__.py')
    f = open(filename, 'w')
    f.close()

