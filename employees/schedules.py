from employees.services import AutomatedPayrollService
from background_task import background

@background
def run_payroll_service():
    service = AutomatedPayrollService()
    service.run()