import django_filters

from . import models


class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = models.Employee
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains'],
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
            'salary': ['exact'],
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

class ContractFilter(django_filters.FilterSet):
    class Meta:
        model = models.Contract
        fields = {
            'department': ['exact'],
            'nature_of_employment': ['exact'],
            'employee__last_name': ['icontains']
        }