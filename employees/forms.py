
import datetime

from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


from common_data.forms import BootstrapMixin
from inventory.models import Supplier
from django.db.models import Q

from . import models


class EmployeesSettingsForm(forms.ModelForm, BootstrapMixin):
    automate_payroll_for = forms.ModelMultipleChoiceField(
        models.Employee.objects.all(), 
        widget = forms.CheckboxSelectMultiple
    )
    #when running payroll - a message must be raised that the hours of 
    #hourly workers must be calculated first
    class Meta:
        model = models.EmployeesSettings
        exclude = "last_payroll_date",


#named benefits on the front end
class AllowanceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Allowance

    
class CommissionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.CommissionRule

class DeductionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Deduction


class PayGradeForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.PayGrade

class CreateEmployeeUserForm(BootstrapMixin, forms.Form):
    employee = forms.ModelChoiceField(models.Employee.objects.all(), widget=forms.HiddenInput)
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        name = cleaned_data['username']
        if User.objects.filter(username=name).exists():
            raise forms.ValidationError('The username selected is already in use')

        if password != cleaned_data['confirm_password']:
            raise forms.ValidationError(' The new passwords do not match')

        usr = User.objects.create_user(name)
        usr.set_password(password)
        usr.save()
        employee = cleaned_data['employee']
        employee.user= usr
        employee.save()

        return cleaned_data 

class EmployeePasswordResetForm(BootstrapMixin, forms.Form):
    employee = forms.ModelChoiceField(models.Employee.objects.all(), widget=forms.HiddenInput)
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        usr = cleaned_data['employee'].user
        new_password = cleaned_data['new_password']
        '''
        if not usr.check_password(cleaned_data['old_password']):
            raise forms.ValidationError('The old password is incorrect')
        '''
        if new_password != cleaned_data['confirm_new_password']:
            raise forms.ValidationError(' The new passwords do not match')

        usr.set_password(new_password)
        usr.save()

        return cleaned_data 

class EmployeeForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active", 'user',
        model = models.Employee

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Personal', 
                    'first_name',
                    'last_name',
                    'address',
                    'email',
                    'phone'),
                Tab('Employee Details', 
                    'hire_date',
                    'title',
                    'pay_grade',
                    'leave_days',
                    'pin',
                    'uses_timesheet'
                    )))
        self.helper.add_input(Submit('submit', 'Submit'))



class PayrollTaxForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.PayrollTax
        fields = '__all__'


class TimesheetForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.EmployeeTimeSheet
        fields = "__all__"

class PayrollOfficerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.PayrollOfficer


class TimeLoggerForm(BootstrapMixin, forms.Form):
    employee_number = forms.IntegerField()
    pin = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        e_num = cleaned_data['employee_number']
        if not models.Employee.objects.filter(pk=e_num).exists():
            raise forms.ValidationError('The selected Employee number is invalid')
        
        employee = models.Employee.objects.get(pk=e_num)

        if cleaned_data['pin'] != employee.pin:
            raise forms.ValidationError('Incorrect pin used for employee')

        # check if a timesheet for this employee for this month exists, if not 
        # create a new one. Check if today has a attendance line if not create a new 
        # one. Check if this line has been logged in, if so log out if not log in.
        TODAY = datetime.date.today()
        NOW = datetime.datetime.now().time()
        sheet_filters = Q(Q(employee=employee) & 
                Q(month=TODAY.month) &
                Q(year=TODAY.year))
        if models.EmployeeTimeSheet.objects.filter(sheet_filters).exists():
            curr_sheet = models.EmployeeTimeSheet.objects.get(sheet_filters)
        else:
            curr_sheet = models.EmployeeTimeSheet.objects.create(
                employee=employee, 
                month=TODAY.month,
                year=TODAY.year
                )
        
        if models.AttendanceLine.objects.filter(
                Q(timesheet=curr_sheet) &
                Q(date=TODAY)
                ).exists():
                
            curr_line = models.AttendanceLine.objects.get(
                Q(timesheet=curr_sheet) &
                Q(date=TODAY)
                )
        else:
            curr_line = models.AttendanceLine.objects.create(
                timesheet=curr_sheet,
                date=TODAY
                )

        if curr_line.time_in is None:
            curr_line.time_in = NOW
            curr_line.save()

        else:
            curr_line.time_out = NOW
            curr_line.save()


class PayrollForm(BootstrapMixin, forms.Form):
    start_period = forms.DateField()
    end_period = forms.DateField()
    employees = forms.ModelMultipleChoiceField(models.Employee.objects.all())


class LeaveRequestForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.Leave
        exclude = 'status', 'authorized_by'

class LeaveAuthorizationForm(BootstrapMixin, forms.Form):
    leave_request = forms.ModelChoiceField(models.Leave.objects.all(), 
        widget=forms.HiddenInput)
    status = forms.ChoiceField(choices = [
        (1, 'Approved'),
        (2, 'Declined')
        ])
    notes = forms.CharField(widget=forms.Textarea, required=False)    
    '''
        filter(
            Q(payrollofficer__isnull=False)) & 
            Q(user__isnull=False)
    '''
    authorized_by = forms.ModelChoiceField(
        models.Employee.objects.all())
    password = forms.CharField(widget=forms.PasswordInput)
    

    def clean(self):
        cleaned_data = super().clean()
        usr = cleaned_data['authorized_by'].user
        authenticated = authenticate(
            username=usr.username,
            password=cleaned_data['password']
        )
        if not authenticated:
            raise forms.ValidationError('You entered an incorrect password for this form')

        return cleaned_data
        
