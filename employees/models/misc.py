from django.db import models
from common_data.models import SingletonModel

class PayrollOfficer(models.Model):
    employee = models.OneToOneField('employees.Employee', on_delete=models.SET_NULL, null=True)
    can_log_timesheets = models.BooleanField(default=False, blank=True)
    can_run_payroll = models.BooleanField(default=False, blank=True)
    can_create_payroll_elements = models.BooleanField(default=False, blank=True)
    can_register_new_employees = models.BooleanField(default=False, blank=True)


class EmployeesSettings(SingletonModel):
    PAYROLL_DATE_CHOICES = [(i, i) for i in range(1, 29)]
    PAYROLL_CYCLE_CHOICES = [
        ('weekly', 'Weekly'), 
        ('bi-monthly', 'Bi-monthly'), 
        ('monthly', 'Monthly')
        ]
    payroll_date_one = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES
        )
    payroll_date_two = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES,
        blank=True, null=True
    )
    payroll_date_three = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES,
        blank=True, null=True
    )
    payroll_date_four = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES,
        blank=True, null=True
    )
    last_payroll_date = models.DateField(blank=True, null=True)
    payroll_cycle = models.CharField(
        max_length=12, 
        choices = PAYROLL_CYCLE_CHOICES
        )
    automate_payroll_for = models.ManyToManyField('employees.Employee', blank=True)
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
