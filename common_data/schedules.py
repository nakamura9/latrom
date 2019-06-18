import subprocess
from background_task import background
from background_task.models import Task
import os 
from latrom import settings
from common_data.models import GlobalConfig

@background(schedule=60)
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


mapping = {
    'D': Task.DAILY,
    'W': Task.WEEKLY,
    'M': Task.MONTHLY
}

config = GlobalConfig.objects.first()

backup_db(repeat=mapping[config.backup_frequency])
