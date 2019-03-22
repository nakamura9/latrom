import django_filters

from . import models


class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = models.Employee
        fields = {
            'title': ['icontains'],
            'first_name': ['icontains'],
        }


class PayslipFilter(django_filters.FilterSet):
    class Meta:
        model = models.Payslip
        fields = {
            'pay_roll_id': ['icontains'],
            'employee': ['exact'],
            'start_period': ['gt'],
            'end_period': ['lt'],
            'status': ['exact']
        }

class TimeSheetFilter(django_filters.FilterSet):
    class Meta:
        model = models.EmployeeTimeSheet
        fields = {
            'year': ['exact'],
            'month': ['exact'],
            'employee': ['exact'],
        }


class PayGradeFilter(django_filters.FilterSet):
    class Meta:
        model = models.PayGrade
        fields = {
            'name': ['icontains'],
            'monthly_salary': ['exact'],
        }


class PayrollOfficerFilter(django_filters.FilterSet):
    class Meta:
        model = models.PayrollOfficer
        fields = {
            'employee': ['exact']
        }

class PayrollTaxFilter(django_filters.FilterSet):
    class Meta:
        model = models.PayrollTax
        fields = {
            'name': ['icontains'],
            'paid_by': ['exact']
        }

class LeaveRequestFilter(django_filters.FilterSet):
    class Meta:
        model = models.Leave
        fields = {
            'start_date': ['exact'],
            'employee': ['exact'],
            'status': ['exact']
        }


class PayrollDateFilter(django_filters.FilterSet):
    class Meta:
        model = models.PayrollDate
        fields = {
            'date': ['exact']
        }