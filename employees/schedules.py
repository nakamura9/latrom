from employees.services import AutomatedPayrollService
from background_task import background
from background_task.models import Task

@background(schedule=60)
def run_payroll_service():
    service = AutomatedPayrollService()
    service.run()

run_payroll_service(repeat=Task.DAILY)