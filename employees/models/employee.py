
import random
import datetime
import calendar
from decimal import Decimal as D
from functools import reduce
from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel, SoftDeletionModel
import planner
import accounting
import invoicing
from employees.models.payslip import Payslip
from employees.models.timesheets import EmployeeTimeSheet,AttendanceLine

import employees
from employees.models.misc import PayrollOfficer
from django.shortcuts import reverse
from common_data.utilities.mixins import ContactsMixin

class Employee(ContactsMixin, Person, SoftDeletionModel):
    email_fields = ['email']
    phone_fields = ['phone']
    '''
    Represents an individual employee of the business. Records their personal 
    details as well as their title, pay grade and leave days.

    properties
    ------------
    deductions_YTD - a field that calculates all the deductions throughout the 
    year. 
        Used in payslips
    allowances_YTD - a field that calculates all the allowances earned 
    throughout the year. 
        Used in payslips
    earnings_YTD - a field that calculates all the  earnings throughout the 
    year. 
        Used in payslips
    is_<role> - checks the instance for evidence that an employee has been 
    assigned a certain role within the system.
    '''

    GENDER_CHOICES = [('male','Male'),('female','Female')]
    

    employee_number = models.AutoField(primary_key=True)
    pay_grade = models.ForeignKey('employees.PayGrade', 
        on_delete=models.CASCADE, blank=True, null=True)
    leave_days = models.FloatField(default=0)
    last_leave_day_increment = models.DateField(null=True)
    uses_timesheet = models.BooleanField(default=False, blank=True)
    user = models.OneToOneField('auth.User', null=True,
         on_delete=models.CASCADE)#not all are users
    pin = models.PositiveSmallIntegerField(default=1000)
    date_of_birth = models.DateField(null=True)
    id_number = models.CharField(max_length=64, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    social_security_number = models.CharField(max_length=255, blank=True, 
        default="")
   
    
    @property
    def latest_timesheet(self):
        qs =EmployeeTimeSheet.objects.filter(employee=self)
        
        return EmployeeTimeSheet.objects.filter(employee=self).latest('pk').pk

    @property
    def short_name(self):
        return f"{self.first_name[0]}. {self.last_name}" 

    def get_absolute_url(self):
        return reverse("employees:employee-detail", kwargs={"pk": self.pk})
    
    def get_earnings_for_month(self, start):
        earnings = 0
        last_day = calendar.monthrange(start.year, start.month)
        end = datetime.date(start.year, start.month, last_day[1])
        #using end period for payslips
        slips = Payslip.objects.filter(end_period__gte=start, 
            end_period__lte=end, 
            status__in=['verified', 'paid'])
        earnings += sum([i.paygrade_['salary'] for i in slips])

        return earnings
    
    def get_nps_earnings(self, start):
        #get total earnings in month
        earnings = self.get_earnings_for_month(start)
        
        if earnings < D(700.0):
            return earnings

        return D(700.0)

    
    def total_nps(self, start):
        insurable_earnings = self.get_nps_earnings(start)
        
        return D(insurable_earnings) * D(0.07)

    def increment_leave_days(self, days):
        self.leave_days += days
        self.last_leave_day_increment = datetime.date.today()
        if self.pay_grade and \
                self.leave_days > self.pay_grade.maximum_leave_days:
            self.leave_days = self.pay_grade.maximum_leave_days
        
        self.save()

    def deduct_leave_days(self, days):
        self.leave_days -= days
        self.save()

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def _payslips_YTD(self):
        '''internal abstract method used in the following properties'''
        curr_year = datetime.date.today().year
        start = datetime.date(curr_year, 1, 1)
        end = datetime.date(curr_year,12,31)
        
        return Payslip.objects.filter(Q(employee=self) \
            & Q(start_period__gte=start) \
            & Q(end_period__lte=end)
            & Q(status="verified"))
    
    @property
    def deductions_YTD(self):
        slips = self._payslips_YTD
        return sum([i.total_deductions for i in slips])

    @property
    def earnings_YTD(self):
        slips = self._payslips_YTD
        return sum([i.gross_pay for i in slips])    

    @property
    def is_sales_rep(self):
        return(invoicing.models.SalesRepresentative.objects.filter(employee=self).exists())

    @property
    def is_inventory_controller(self):
        return hasattr(self, 'inventorycontroller')

    @property
    def is_bookkeeper(self):
        return(accounting.models.Bookkeeper.objects.filter(employee=self).exists())
        

    @property
    def is_payroll_officer(self):
        return(PayrollOfficer.objects.filter(employee=self).exists())


    @property
    def is_serviceperson(self):
        return hasattr(self, 'serviceperson')

    @property
    def is_manufacturing_associate(self):
        return hasattr(self, 'manufacturingassociate')

    @property
    def agenda_items(self):
        #check participants as well
        filter = None
        if self.user:
            filter = Q(Q(owner=self.user) | Q(eventparticipant__employee=self))
        else:
            filter = Q(eventparticipant__employee=self)
        return planner.models.Event.objects.filter(
            Q(Q(completed=False) & Q(date__gte=datetime.date.today())) & 
            filter).count()


    @property
    def missed_events(self):
        #check participants as well
        filter = None
        if self.user:
            filter = Q(Q(owner=self.user) | Q(eventparticipant__employee=self))
        else:
            filter = Q(eventparticipant__employee=self)
        return planner.models.Event.objects.filter(
            Q(Q(completed=False) & Q(date__lt=datetime.date.today())) & 
            filter).count()

    @property
    def attendance(self):
        TODAY = datetime.date.today()
        
        if EmployeeTimeSheet.objects.filter(
                employee=self, 
                year=TODAY.year, 
                month=TODAY.month).exists():
            sheet = EmployeeTimeSheet.objects.get(
                                    employee=self, 
                                    year=TODAY.year, 
                                    month=TODAY.month)

            attendance = []
            for i in range(1,32):
                try:
                    date = datetime.date(TODAY.year, TODAY.month, i)
                except:
                    attendance.append(2)
                    continue
                else:
                    if AttendanceLine.objects.filter(
                                date=date, timesheet=sheet).exists():
                        attendance.append(0)
                    else:
                        attendance.append(2)

            return attendance

        else:
            return list(range(1,32))

class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    manager = models.ForeignKey('employees.employee', on_delete=models.SET_NULL, related_name="manager", null=True)
    employees = models.ManyToManyField('employees.employee',
        related_name="employees")
    parent_department = models.ForeignKey('employees.department', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("employees:department-detail", kwargs={"pk": self.pk})
    

    @property
    def children(self):
        return Department.objects.filter(parent_department=self)

class Termination(models.Model):
    TERMINATION_REASONS = [
        ('R', 'Retirement'),
        ('C', 'Casual Employee'),
        ('D', 'Death'),
        ('O', 'Other')
    ]
    date = models.DateField()
    reason_for_termination = models.CharField(max_length=1, default='R', 
        choices=TERMINATION_REASONS)
    contract = models.OneToOneField('employees.Contract', null=True, 
        blank=True,on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("employees:contract-details", kwargs={
            "pk": self.contract.pk
        })
    
    @property
    def reason_string(self):
        return dict(self.TERMINATION_REASONS)[self.reason_for_termination]
class Contract(models.Model):
    NATURE_OF_EMPLOYMENT = [
        ('A', 'Arduous'),
        ('N', 'Normal')
    ]

    EMPLOYEE_CATEGORIES = [
        ('Temporary', 'Temporary Employee'),
        ('Subcontractor', 'Subcontractor'),
        ('Permanent Employee', 'Permanent Employee')
    ]
    start_date = models.DateField()
    department = models.ForeignKey('employees.Department', null=True, 
        blank=True,on_delete=models.SET_NULL)
    employee = models.ForeignKey('employees.Employee', null=True, 
        blank=True,on_delete=models.SET_NULL)
    job_position = models.CharField(max_length=255, blank=True)
    end_of_probation = models.DateField()
    termination_date = models.DateField(blank=True, null=True)
    employee_category = models.CharField(max_length=64, 
        choices=EMPLOYEE_CATEGORIES)
    nature_of_employment = models.CharField(max_length=1, default='N', 
        choices=NATURE_OF_EMPLOYMENT)

    def get_absolute_url(self):
        return reverse("employees:contract-details", kwargs={"pk": self.pk})
    
    @property
    def nature_of_employment_string(self):
        return dict(self.NATURE_OF_EMPLOYMENT)[self.nature_of_employment]

    