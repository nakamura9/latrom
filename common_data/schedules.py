import subprocess
from background_task import background
from background_task.models import Task
import os 
from latrom import settings
from common_data.models import GlobalConfig
from common_data.utilities.db_util import DBBackupService

@background
def backup_db():
    DBBackupService().run()

try:
    backup_db(repeat=Task.DAILY)
except:
    # TODO handle exceptions better
    pass
