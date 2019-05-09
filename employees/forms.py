
import datetime

from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Fieldset, 
                                Layout, 
                                Submit, 
                                Row, 
                                Column,
                                HTML)
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from common_data.forms import BootstrapMixin
from inventory.models import Supplier
from accounting.models import Account
from django.db.models import Q
from django.forms import ValidationError
from . import models



class EmployeesSettingsForm(forms.ModelForm, BootstrapMixin):
    #when running payroll - a message must be raised that the hours of 
    #hourly workers must be calculated first
    class Meta:
        model = models.EmployeesSettings
        exclude = "last_payroll_date", 'is_configured', 'service_hash'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

#named benefits on the front end
class AllowanceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Allowance

class AllowanceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active", 'amount', 'taxable' 
        model = models.Allowance
    
class CommissionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.CommissionRule

class CommissionUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active", " min_sales", "rate"
        model = models.CommissionRule

class DeductionForm(forms.ModelForm, BootstrapMixin):
    #only allow deduction accounts for 
    account_paid_into = forms.ModelChoiceField(Account.objects.filter(Q(type="liability") | Q(type="expense")), required=False)
    class Meta:
        exclude="active",
        model = models.Deduction

class DeductionUpdateForm(forms.ModelForm, BootstrapMixin):
    account_paid_into = forms.ModelChoiceField(Account.objects.filter(
        Q(type="liability") | Q(type="expense")), required=False)
    class Meta:
        fields = "name",
        model = models.Deduction


class PayGradeForm(forms.ModelForm, BootstrapMixin):
    allowances = forms.ModelMultipleChoiceField(models.Allowance.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    deductions = forms.ModelMultipleChoiceField(models.Deduction.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    payroll_taxes = forms.ModelMultipleChoiceField(
        models.PayrollTax.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    class Meta:
        fields = "__all__"
        model = models.PayGrade

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    'name',
                    'monthly_leave_days',
                    Row(
                        Column('salary', css_class='form-group col-6'),
                        Column('pay_frequency', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('hourly_rate', css_class='form-group col-4'),
                        Column('overtime_rate', css_class='form-group col-4'),
                        Column('overtime_two_rate', css_class='form-group col-4'),                        
                    ),
                    Row(
                        Column('commission', css_class='form-group col-6'),
                        Column('lunch_duration', css_class='form-group col-6'),
                    ),
                    'subtract_lunch_time_from_working_hours',
                ),
                Tab('allowances',
                    'allowances',
                ),
                Tab('deductions',
                    'deductions',
                ),
                Tab('payroll taxes',
                    'payroll_taxes',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

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
    pay_grade = forms.ModelChoiceField(models.PayGrade.objects.all(), 
        required=False)
    class Meta:
        exclude="active", 'user','last_leave_day_increment'
        model = models.Employee

        widgets = {
                'address':forms.Textarea(attrs={'rows':4, 'cols':15}), 
            }

    date_of_birth = forms.DateField(required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic', 
                    Row(
                        Column('first_name', css_class='form-group col-6'),
                        Column('last_name', css_class='form-group col-6'),
                    ), 
                    Row(
                        Column('hire_date', 'title', css_class='form-group col-6'),
                        Column('address', css_class='form-group col-6'),
                    ),
                    'email',
                    'phone'
                    ),
                    Tab('Other',
                        'date_of_birth',
                        'id_number',
                        'gender',
                        'pay_grade',
                        'leave_days',
                        'pin',
                        'uses_timesheet'
                    )))
        self.helper.add_input(Submit('submit', 'Submit'))

    def save(self, *args, **kwargs):
        '''The very first employee created in the application is automatically assigned a user.'''
        resp = super().save(*args, **kwargs)
        if models.Employee.objects.all().count() == 1:
            user = User.objects.create(
                username=self.instance.first_name,
                password="1234"
            )
            self.instance.user = user
            self.instance.save()

        return resp


class EmployeePortalForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields=['first_name', 'last_name', 'address', 'email', 'phone', 'date_of_birth', 'gender', 'id_number']
        model = models.Employee

        widgets = {
                'address':forms.Textarea(attrs={'rows':4, 'cols':15}), 
            }
class PayrollTaxForm(forms.ModelForm, BootstrapMixin):
    brackets = forms.CharField(required=True, widget=forms.HiddenInput)
    
    class Meta:
        model = models.PayrollTax
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(). __init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Payroll Tax Details',
                    'brackets',
                    'name',
                    'paid_by',
                ),
                Tab('Tax Brackets',
                    HTML(
                        """
            <div id="tax-brackets"></div>                        
                        """
                    )
                )
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class TimesheetForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.EmployeeTimeSheet
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('employee', css_class='form group col-3'),
                Column('month', css_class='form group col-3'),
                Column('year', css_class='form group col-3'),
                Column('recorded_by', css_class='form group col-3'),
            ),
            HTML(
                """
                <div class="col-sm-12" id="timesheet-root">
                </div>
                """
            ),
            'complete',
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class PayrollOfficerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.PayrollOfficer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

class PayrollOfficerUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "employee",
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


class TimeLoggerFormWithEmployee(TimeLoggerForm):
    employee_number = forms.IntegerField(widget=forms.HiddenInput)



class PayrollForm(BootstrapMixin, forms.Form):
    start_period = forms.DateField()
    end_period = forms.DateField()
    payroll_officer = forms.ModelChoiceField(
        models.Employee.objects.filter(payrollofficer__isnull=False))
    employees = forms.ModelMultipleChoiceField(
        models.Employee.objects.all(),
        widget= forms.CheckboxSelectMultiple)


class LeaveRequestForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.Leave
        exclude = 'status', 'authorized_by', 'recorded'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    Row(
                        Column('start_date', css_class='form-group col-6'),
                        Column('end_date', css_class='form-group col-6'),
                    ),
                    'employee',
                    'category',
                ),
                Tab('notes',
                    'notes',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class LeaveAuthorizationForm(BootstrapMixin, forms.Form):
    leave_request = forms.ModelChoiceField(models.Leave.objects.all(), 
        widget=forms.HiddenInput)
    status = forms.ChoiceField(choices = [
        (1, 'Approved'),
        (2, 'Declined')
        ])
    notes = forms.CharField(widget=forms.Textarea, required=False)    
    
    authorized_by = forms.ModelChoiceField(models.PayrollOfficer.objects.all())
    password = forms.CharField(widget=forms.PasswordInput)
    

    def clean(self):
        cleaned_data = super().clean()
        usr = cleaned_data['authorized_by'].employee.user
        if not usr:
            raise forms.ValidationError('The officer selected has no user profile')

         
        if not authenticate(username=usr.username,
                password=cleaned_data['password']):
            raise forms.ValidationError('You entered an incorrect password for this form')

        return cleaned_data

class PayrollDateForm(forms.ModelForm, BootstrapMixin):
    schedule = forms.ModelChoiceField(models.PayrollSchedule.objects.all(), widget=forms.HiddenInput)
    employees = forms.ModelMultipleChoiceField(
        models.Employee.objects.all(), 
        widget = forms.CheckboxSelectMultiple,
        required=False
    )
    departments = forms.ModelMultipleChoiceField(
        models.Department.objects.all(), 
        widget = forms.CheckboxSelectMultiple,
        required=False
    )
    pay_grades = forms.ModelMultipleChoiceField(
        models.PayGrade.objects.all(), 
        widget = forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        fields = "__all__"
        model = models.PayrollDate

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('(Employees)',
                    'schedule',
                    'date',
                    'employees'
                ),
                Tab('(Departments)',
                    'departments'
                ),
                Tab('(Pay Grades)',
                    'pay_grades'
                ),
            )
        )

        self.helper.add_input(Submit('submit', 'Submit'))


class DepartmentForm(forms.ModelForm, BootstrapMixin):
    employees = forms.ModelMultipleChoiceField(models.Employee.objects.all(),
        widget=forms.CheckboxSelectMultiple)
    class Meta:
        fields = "__all__"
        model = models.Department

        widgets = {
                'description':forms.Textarea(attrs={'rows':4, 'cols':15}), 
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    'name',
                    'manager',
                    'description',
                    'parent_department',

                ),
                Tab('members',
                    'employees'
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class EmployeeAuthenticateForm(BootstrapMixin, forms.Form):
    employee = forms.ModelChoiceField(models.Employee.objects.all())
    pin = forms.CharField(widget = forms.NumberInput)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        if int(cleaned_data['pin']) != cleaned_data['employee'].pin:
            raise ValidationError('The Pin supplied is incorrect')

        return cleaned_data