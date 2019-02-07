import datetime
import decimal
import json
import os
import urllib

from django.shortcuts import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import User

from employees.models import *
from latrom import settings
from accounting.models import Account, JournalEntry
from .models import create_test_employees_models

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()


class GenericPageTests(TestCase):
    fixtures = ['accounts.json', 'employees']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_employees_page(self):
        resp = self.client.get(reverse('employees:dashboard'))
        self.assertTrue(resp.status_code == 200)

    def test_get_util_list_page(self):
        resp = self.client.get(reverse('employees:util-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_automated_config_page(self):
        resp = self.client.get(reverse('employees:config',
            kwargs={
                'pk':1
                }))
        self.assertTrue(resp.status_code == 200)

    def test_get_manual_config_page(self):
        resp = self.client.get(reverse('employees:manual-config'))
        self.assertTrue(resp.status_code == 200)

class PayGradePageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.PAYGRADE_DATA = {
            'name': 'Other Test Grade',
            'monthly_salary': 0,
            'monthly_leave_days': 1.5,
            'hourly_rate': 1.5,
            'overtime_rate': 2.25,
            'overtime_two_rate': 3,
            'commission': cls.commission.pk,
            'allowances': cls.allowance.pk,
            'deductions': cls.deduction.pk,
            'lunch_duration': '0:15:00'
        }

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_pay_grade_list_page(self):
        resp = self.client.get(reverse('employees:list-pay-grades'))
        self.assertEqual(resp.status_code, 200)

    def test_get_pay_grade_create_page(self):
        resp = self.client.get(reverse('employees:create-pay-grade'))
        self.assertEqual(resp.status_code, 200)

    def test_post_pay_grade_create_page(self):
        resp = self.client.post(reverse('employees:create-pay-grade'),
            data=self.PAYGRADE_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_update_pay_grade_page(self):
        resp = self.client.get(reverse('employees:update-pay-grade', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_pay_grade_page(self):
        resp = self.client.post(reverse('employees:update-pay-grade', kwargs={
            'pk': 1
        }), data=self.PAYGRADE_DATA)

        self.assertEqual(resp.status_code, 302)


class PaySlipPageTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'journals.json', 'employees.json', 
        'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        create_test_employees_models(cls)
        
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_pay_slips_list_page(self):
        resp = self.client.get(reverse('employees:list-pay-slips'))
        self.assertEqual(resp.status_code, 200)

    def test_get_pay_slip_detail_page(self):
        resp = self.client.get(reverse('employees:pay-slip-detail', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_delete_payslip_page_get(self):
        resp = self.client.get('/employees/pay-slip-delete/1')
        self.assertEqual(resp.status_code, 200)

    def test_delete_payslip_page_post(self):
        second_slip = Payslip.objects.create(
        start_period=TODAY,
            end_period=TODAY,
            employee=self.employee,
            normal_hours=100,
            overtime_one_hours=0,
            overtime_two_hours=0,
            pay_roll_id = 1,
            pay_grade = self.employee.pay_grade
    )
        resp = self.client.post('/employees/pay-slip-delete/2')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Payslip.objects.all().count(), 1)

    def test_payslip_verify_page(self):
        resp = self.client.get('/employees/pay-slip-verify/1')
        self.assertEqual(resp.status_code, 200)

    def test_payslip_verify_status(self):
        resp = self.client.get('/employees/pay-slip-verify-status/1')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Payslip.objects.get(pk=1).status, 'verified')

    def test_execute_payroll(self):
        settings = EmployeesSettings.objects.first()
        settings.payroll_officer = Employee.objects.first()
        settings.save()

        prev_entry_count = JournalEntry.objects.all().count()
        self.slip.status = 'verified'
        self.slip.save()
        resp = self.client.get('/employees/execute-payroll')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(prev_entry_count != JournalEntry.objects.all().count())


class EmployeePageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        cls.EMPLOYEE_DATA = {
                'first_name': 'Unit',
                'last_name': 'Test',
                'address': 'some test place',
                'email': 'test@mail.com',
                'phone': '123456789',
                'title': 'manager',
                'pay_grade': cls.grade.pk,
                'hire_date': TODAY,
                'leave_days': 0,
                'pin': 1000
                }

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')
    
    def test_get_list_employees_page(self):
        resp = self.client.get(reverse('employees:list-employees'))
        self.assertEqual(resp.status_code, 200)


    def test_get_create_employee_page(self):
        resp = self.client.get(reverse('employees:create-employee'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_employee_page(self):
        resp = self.client.post(reverse('employees:create-employee'),
            data=self.EMPLOYEE_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_employee_update_page(self):
        resp = self.client.get(reverse('employees:employee-update',
             kwargs={'pk': 1}))
        self.assertTrue(resp.status_code==200)

    def test_post_employee_update_page(self):
        resp = self.client.post(reverse('employees:employee-update',
            kwargs={
                'pk': 1
            }), data=self.EMPLOYEE_DATA)

        self.assertTrue(resp.status_code == 302)

    def test_get_employee_detail_page(self):
        resp = self.client.get(reverse('employees:employee-detail', 
            kwargs={'pk': 1}))
        self.assertTrue(resp.status_code==200)
    
    def test_get_employee_delete_page(self):
        resp = self.client.get(reverse('employees:employee-delete', 
            kwargs={'pk': 1}))
        self.assertTrue(resp.status_code==200)

    def test_post_employee_delete_page(self):
        post_data = dict(self.EMPLOYEE_DATA)
        post_data['pay_grade'] = self.grade
        Employee.objects.create(**post_data)
        resp = self.client.post(reverse('employees:employee-delete', 
            kwargs={'pk': Employee.objects.latest('pk').pk}))
        self.assertTrue(resp.status_code==302)

    def test_employees_create_user_page_get(self):
        resp = self.client.get('/employees/employee/create-user/1')
        self.assertEqual(resp.status_code, 200)

    def test_employees_create_user_page_post(self):
        resp = self.client.post('/employees/employee/create-user/1',
            data={
                'employee': 1,
                'username': 'name',
                'password': 'password',
                'confirm_password': 'password'
            })
        self.assertEqual(resp.status_code, 302)

    def test_employees_create_user_page_post_with_error(self):
        resp = self.client.post('/employees/employee/create-user/1',
            data={
                'employee': 1,
                'username': 'name',
                'password': 'passw0rd',
                'confirm_password': 'password'
            })
        #error has a 200 status code
        self.assertEqual(resp.status_code, 200)

    def test_employees_get_reset_password_page(self):
        resp = self.client.get('/employees/employee/user/reset-password/1')
        self.assertEqual(resp.status_code, 200)

    def test_employees_reset_password_page_post(self):
        if not self.employee.user:
            usr = User.objects.create_user('name')
            usr.set_password('password')
            usr.save()
        self.employee.user = usr
        self.employee.save()
        resp = self.client.post('/employees/employee/user/reset-password/1',
            data={
                'employee': 1,
                'old_password': 'password',
                'new_password': 'new_password',
                'confirm_new_password': 'new_password'
            })
        self.assertEqual(resp.status_code, 302)

    def test_employees_delete_user_post(self):
        resp = self.client.get('/employees/employee/delete-user/1')
        self.assertEqual(resp.status_code, 302)
        

class BenefitsPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        cls.ALLOWANCE_DATA = {
                'name': 'Other Test Allowance',
                'amount': 100
            }
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_allowance_page(self):
        resp = self.client.get(reverse('employees:create-allowance'))
        self.assertTrue(resp.status_code == 200)

    def test_post_allowance_page(self):
        resp = self.client.post(reverse('employees:create-allowance'),
            data=self.ALLOWANCE_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_allowance_update_page(self):
        resp = self.client.get(reverse('employees:update-allowance',
            kwargs={
                'pk': self.allowance.pk
            }))

    def test_post_allowance_update_page(self):
        resp = self.client.post(reverse('employees:update-allowance',
            kwargs={
                'pk': self.allowance.pk
            }),
                data=self.ALLOWANCE_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_allowance_delete_page(self):
        resp = self.client.get(reverse('employees:delete-allowance',
            kwargs={
                'pk': self.allowance.pk
            }))

    def test_post_allowance_delete_page(self):
        Allowance.objects.create(**self.ALLOWANCE_DATA)
        resp = self.client.post(reverse('employees:delete-allowance',
            kwargs={
                'pk': Allowance.objects.latest('pk').pk
            }))


class CommissionPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        cls.COMMISSION_DATA = {
                'name': 'Test Rule',
                'min_sales': 100,
                'rate': 10
            }
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_commission_rule_create_page(self):
        resp = self.client.get(reverse('employees:create-commission'))
        self.assertTrue(resp.status_code == 200)

    def test_post_commission_rule_page(self):
        resp = self.client.post(reverse('employees:create-commission'),
            data=self.COMMISSION_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_commission_rule_update_page(self):
        resp = self.client.get(reverse('employees:update-commission',
            kwargs={
                'pk': self.commission.pk
            }))

    def test_post_commission__rule_update_page(self):
        resp = self.client.post(reverse('employees:update-commission',
            kwargs={
                'pk': self.commission.pk
            }), data=self.COMMISSION_DATA)

        self.assertTrue(resp.status_code==302)

    def test_get_commission_rule_delete_page(self):
        resp = self.client.get(reverse('employees:delete-commission',
            kwargs={
                'pk': self.commission.pk
            }))

    def test_post_commission_rule_delete_page(self):
        CommissionRule.objects.create(**self.COMMISSION_DATA)
        resp = self.client.post(reverse('employees:delete-commission',
            kwargs={
                'pk': CommissionRule.objects.latest('pk').pk
            }))


class DeductionPageTests(TestCase):
    fixtures = ['accounts.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        cls.DEDUCTION_DATA = {
                'name': 'Other Test Deduction',
                'method': 1,
                'trigger':1,
                'amount': 10,
                'rate': 0,
                'account_paid_into': 5008
            }
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_deduction_page(self):
        resp = self.client.get(reverse('employees:create-deduction'))
        self.assertTrue(resp.status_code == 200)

    def test_post_deduction_page(self):
        resp = self.client.post(reverse('employees:create-deduction'),
            data=self.DEDUCTION_DATA)
        
        self.assertEqual(resp.status_code, 302)
        
    def test_get_deduction_update_page(self):
        resp = self.client.get(reverse('employees:update-deduction',
            kwargs={
                'pk': self.deduction.pk
            }))

    def test_post_deduction_update_page(self):
        resp = self.client.post(reverse('employees:update-deduction',
            kwargs={
                'pk': self.deduction.pk
            }), data=self.DEDUCTION_DATA)

        self.assertEqual(resp.status_code, 302)

    def test_get_deduction_delete(self):
        resp = self.client.get(reverse('employees:delete-deduction',
            kwargs={
                'pk': self.deduction.pk
            }))

    def test_post_deduction_delete(self):
        import copy 
        data = copy.deepcopy(self.DEDUCTION_DATA)
        data['account_paid_into'] = Account.objects.get(pk=5008)
        Deduction.objects.create(**data)
        resp = self.client.post(reverse('employees:delete-deduction',
            kwargs={
                'pk': Deduction.objects.latest('pk').pk
            }))


class PayrollTaxViewTests(TestCase):
    fixtures = ['accounts.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')


    def test_create_payroll_tax_page(self):
        resp = self.client.get('/employees/create-payroll-tax')
        self.assertEqual(resp.status_code, 200)

    def test_create_payroll_tax_page_post(self):
        resp = self.client.post('/employees/create-payroll-tax',
            data={
                'brackets': urllib.parse.quote(json.dumps([{
                    'lower_limit': 0,
                    'upper_limit': 300,
                    'rate': 10,
                    'deduction': 0
                }])),
                'name': 'Name',
                'paid_by': 0
            })
        self.assertEqual(resp.status_code, 302)

    def test_payroll_tax_update_page_get(self):
        resp = self.client.get('/employees/update-payroll-tax/1')
        self.assertEqual(resp.status_code, 200)


    def test_payroll_tax_update_page_post(self):
        resp = self.client.post('/employees/update-payroll-tax/1',
            data={
                'name': 'OtherName',
                'paid_by': 1
            })

        self.assertEqual(resp.status_code, 302)

    def test_get_payroll_tax_list_page(self):
        resp = self.client.get('/employees/payroll-tax-list')
        self.assertEqual(resp.status_code, 200)

    def test_payroll_tax_delete_page_get(self):
        resp = self.client.get('/employees/payroll-tax-delete/1')
        self.assertEqual(resp.status_code, 200)

    def test_payroll_tax_delete_page_get(self):
        other_prt = PayrollTax.objects.create(
            name="name",
            paid_by=0
        )
        resp = self.client.post('/employees/payroll-tax-delete/2')
        self.assertEqual(resp.status_code, 302)


class PayrollOfficerViewTests(TestCase):
    fixtures = ['accounts.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def create_officer(self):
        if not PayrollOfficer.objects.all().count():
            PayrollOfficer.objects.create(
                employee=self.employee
            )

    def test_get_create_payroll_officer_page(self):
        resp = self.client.get('/employees/payroll-officer/create')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_payroll_officer_page(self):
        resp = self.client.post('/employees/payroll-officer/create',
            data={
                'employee': 1
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_payroll_officer_list_page(self):
        resp = self.client.get('/employees/payroll-officer/list')
        self.assertEqual(resp.status_code, 200)

    def test_get_payroll_officer_detail_page(self):
        self.create_officer()

        resp = self.client.get('/employees/payroll-officer/detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_payroll_officer_update_page(self):
        self.create_officer()

        resp = self.client.get('/employees/payroll-officer/update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_payroll_officer_update_page(self):
        self.create_officer()

        resp = self.client.post('/employees/payroll-officer/update/1',
            data={
                'can_log_timesheets': True
            })
        self.assertEqual(resp.status_code, 302)

class LeaveViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.LEAVE_DATA = {
                'start_date': TODAY,
                'end_date': TODAY,
                'employee': 1,
                'category': 1
            }
        Leave.objects.create(
            start_date=TODAY,
            end_date=TODAY,
            employee=cls.employee,
            category=1
            )

        if not cls.employee.user:
            usr = User.objects.create_user('name')
            usr.set_password('password')
            usr.save()
        cls.employee.user = usr
        cls.employee.save()
        cls.officer = PayrollOfficer.objects.create(employee=Employee.objects.first())
        


    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_leave_request_page(self):
        resp = self.client.get('/employees/leave-request')
        self.assertEqual(resp.status_code, 200)
    
    def test_post_leave_request_page(self):
        resp = self.client.post('/employees/leave-request',
            data=self.LEAVE_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_leave_calendar_page(self):
        resp = self.client.get('/employees/leave-calendar/')
        self.assertEqual(resp.status_code, 200)

    def test_get_leave_list_page(self):
        resp = self.client.get('/employees/leave-list')
        self.assertEqual(resp.status_code, 200)

    def test_get_leave_detail(self):

        resp = self.client.get('/employees/leave-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_leave_authorization_page(self):
        resp = self.client.get('/employees/leave-authorization/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_leave_authorization_page(self):
        data = {
                'status': 1,
                'notes': 'Note',
                'password': 'password',
                'authorized_by': 1,
                'leave_request': 1
            }
        resp = self.client.post('/employees/leave-authorization/1',
            data=data
            )
        self.assertEqual(resp.status_code, 302)

    def test_leave_month_api(self):
        resp = self.client.get('/employees/api/month/2018/01')
        self.assertEqual(resp.status_code, 200)

    def test_leave_year_api(self):
        resp = self.client.get('/employees/api/year/2018')
        self.assertEqual(resp.status_code, 200)

class TimesheetViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.timesheet = EmployeeTimeSheet.objects.create(
            employee=cls.employee,
            month=1,
            year=2018,
            recorded_by=cls.employee,
            complete=True
        )
        cls.SHEET_DATA = {
                'employee': 1,
                'month': 1,
                'year': 2018,
                'recorded_by': 1,
                'lines': urllib.parse.quote(json.dumps([
                    {
                        'date': 1,
                        'timeIn': "08:00",
                        'timeOut': '17:00',
                        'breaksTaken': '00:30'
                    }
                ]))
            }

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_timesheet_create_page(self):
        resp = self.client.get('/employees/timesheet/create')
        self.assertEqual(resp.status_code, 200)

    def test_post_timesheet_create_page(self):
        resp = self.client.post('/employees/timesheet/create',
            data=self.SHEET_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_timesheet_list_page(self):
        resp = self.client.get('/employees/timesheet/list')
        self.assertEqual(resp.status_code, 200)

    def test_get_timesheet_detail_page(self):
        resp = self.client.get('/employees/timesheet/detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_timesheet_update_page(self):
        resp = self.client.get('/employees/timesheet/update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_timesheet_update_page(self):
        resp = self.client.post('/employees/timesheet/update/1',
            data=self.SHEET_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_time_logger_page(self):
        resp = self.client.get('/employees/time-logger')
        self.assertEqual(resp.status_code, 200)

    def test_post_time_logger_page(self):
        resp = self.client.post('/employees/time-logger', data={
            'employee_number': 1,
            'pin': 1000
        })
        self.assertEqual(resp.status_code, 302)