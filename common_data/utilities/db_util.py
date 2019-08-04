from common_data.utilities import AutomatedServiceMixin
from common_data.models import GlobalConfig
import subprocess
import os 
from latrom import settings
import datetime


class DBBackupService(AutomatedServiceMixin):
    service_name = 'common'
    
    @property 
    def should_backup_db(self):
        config = GlobalConfig.objects.first()
        now = datetime.datetime.now()
        return (now - config.last_automated_service_run).total_seconds() \
                    >= config.task_mapping


    def _run(self):
        if not self.should_backup_db:
            return 

        os.chdir(settings.BASE_DIR)
        ret = subprocess.run(['python', 'manage.py', 'dbbackup',])
        if ret.returncode != 0:
            raise Exception('Failed to backup db')

        if os.path.exists('debug.log'):
            try:
                os.remove('debug.log')
            except:
                pass
