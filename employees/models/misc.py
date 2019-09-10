from django.db import models
from common_data.models import SingletonModel, SoftDeletionModel
from employees.schedules import run_payroll_service
from background_task.models import Task
from django.shortcuts import reverse

class PayrollOfficer(models.Model):
    employee = models.OneToOneField('employees.Employee', 
        on_delete=models.SET_NULL, 
        null=True)
    can_log_timesheets = models.BooleanField(default=False, blank=True)
    can_run_payroll = models.BooleanField(default=False, blank=True)
    can_create_payroll_elements = models.BooleanField(default=False, blank=True)
    can_register_new_employees = models.BooleanField(default=False, blank=True)

    def get_absolute_url(self):
        return reverse("employees:payroll-officer-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.employee)

class EmployeesSettings(SingletonModel):
    last_payroll_date = models.DateField(blank=True, null=True)
    require_verification_before_posting_payslips = models.BooleanField(
        default=True
        )
    salary_follows_profits = models.BooleanField(default=True)
    payroll_officer = models.ForeignKey("employees.PayrollOfficer", 
        on_delete=models.SET_NULL, null=True,
        related_name="payroll_officer",
        blank=True
    )
    payroll_account = models.ForeignKey(
        'accounting.account',
        on_delete=models.SET_DEFAULT,
        default=1000)
    payroll_counter = models.IntegerField(default=0)
    business_social_security_number = models.CharField(max_length=255, 
        blank=True, default="")
    is_configured = models.BooleanField(default=False)
    service_hash = models.CharField(max_length=255, default="", blank=True)


    