from background_task import background
from accounting.util import AccountingTaskService

@background
def run_accounting_service():
    service = AccountingTaskService()
    service.run()