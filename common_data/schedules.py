import subprocess
from background_task import background
import os 
from latrom import settings

@background
def backup_db():
    os.chdir(settings.BASE_DIR)
    ret = subprocess.run(['python', 'manage.py', 'dbbackup', '-z'])
    if ret.returncode != 0:
        raise Exception('Failed to backup db')

    if os.path.exists('debug.log'):
        try:
            os.remove('debug.log')
        except:
            pass