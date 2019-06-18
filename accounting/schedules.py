from background_task import background
from background_task.models import Task
from accounting.util import AccountingTaskService
from datetime import timedelta

@background(schedule=60)
def run_accounting_service():
    service = AccountingTaskService()
    service.run()

run_accounting_service(repeat=Task.DAILY)