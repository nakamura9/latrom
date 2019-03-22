from django.db import models
from common_data.models import SingletonModel

class PayrollOfficer(models.Model):
    employee = models.OneToOneField('employees.Employee', on_delete=models.SET_NULL, null=True)
    can_log_timesheets = models.BooleanField(default=False, blank=True)
    can_run_payroll = models.BooleanField(default=False, blank=True)
    can_create_payroll_elements = models.BooleanField(default=False, blank=True)
    can_register_new_employees = models.BooleanField(default=False, blank=True)


class EmployeesSettings(SingletonModel):
    last_payroll_date = models.DateField(blank=True, null=True)
    require_verification_before_posting_payslips = models.BooleanField(
        default=True
        )
    salary_follows_profits = models.BooleanField(default=True)
    payroll_officer = models.ForeignKey("employees.Employee", 
        on_delete=models.SET_NULL, null=True,
        related_name="payroll_officer",
        blank=True, 
        limit_choices_to={'payrollofficer__isnull': False}
    )
    payroll_account = models.ForeignKey(
        'accounting.account',
        on_delete=models.SET_DEFAULT,
        default=1000)
    payroll_counter = models.IntegerField(default=0)
