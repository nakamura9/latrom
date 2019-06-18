from background_task import background
from background_task.models import Task
from accounting.util import AccountingTaskService
from datetime import timedelta

@background
def run_accounting_service():
    service = AccountingTaskService()
    service.run()

try:
    run_accounting_service(repeat=Task.DAILY)
except:
    # TODO handle exceptions better
    pass