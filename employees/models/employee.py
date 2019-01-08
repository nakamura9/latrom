
import random
import datetime
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


class Employee(Person, SoftDeletionModel):
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
    employee_number = models.AutoField(primary_key=True)
    hire_date = models.DateField()
    title = models.CharField(max_length=32)
    pay_grade = models.ForeignKey('employees.PayGrade', 
        on_delete=models.CASCADE,default=1)
    leave_days = models.FloatField(default=0)
    last_leave_day_increment = models.DateField(null=True)
    uses_timesheet = models.BooleanField(default=False, blank=True)
    user = models.OneToOneField('auth.User', null=True,
         on_delete=models.CASCADE)#not all are users
    pin = models.PositiveSmallIntegerField(default=1000)
    

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
        return reduce(lambda x, y: x + y, [i.total_deductions \
             for i in slips], 0)

    @property
    def earnings_YTD(self):
        slips = self._payslips_YTD
        return reduce(lambda x, y: x + y, [i.gross_pay \
             for i in slips], 0)    

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
        return planner.models.Event.objects.filter(
            Q(Q(completed=False) & Q(date__gte=datetime.date.today())) &
            Q(owner=self.user)).count()