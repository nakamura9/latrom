import datetime
import decimal
import json
import os
import urllib

from django.shortcuts import reverse
from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

from employees.models import *
from accounting.models import Account, JournalEntry
from .models import create_test_employees_models
import common_data
from calendar import monthrange
from employees.views import (
    EmployeeAttendanceReportPDFView,
    PayslipPDFView,
    PayrollPDFReport,
    LeaveReportPDFView)

TODAY = datetime.date.today()


class GenericPageTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'employees.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        common_data.tests.test_models.create_test_common_entities(cls)
        

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_employees_page(self):
        resp = self.client.get(reverse('employees:dashboard'))
        self.assertTrue(resp.status_code == 302)
        settings = EmployeesSettings.objects.first()
        settings.is_configured = True
        settings.save()
        resp = self.client.get(reverse('employees:dashboard'))
        self.assertTrue(resp.status_code == 200)
        settings.is_configured = False
        settings.save()


    def test_get_automated_config_page(self):
        resp = self.client.get(reverse('employees:config',
            kwargs={
                'pk':1
                }))
        self.assertTrue(resp.status_code == 200)

    def test_get_manual_config_page(self):
        resp = self.client.get(reverse('employees:manual-config'))
        self.assertTrue(resp.status_code == 200)

    def test_post_manual_config_employees(self):
        today = datetime.date.today()
        start, end = monthrange(today.year, today.month)
        
        resp = self.client.post(reverse('employees:manual-config'), 
            data={
                'start_period': start,
                'end_period': end,
                'payroll_officer': 1,
                'employees': ['1']
            })




class PayGradePageTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json']


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.PAYGRADE_DATA = {
            'name': 'Other Test Grade',
            'salary': 0,
            'monthly_leave_days': 1.5,
            'maximum_leave_days': 20,
            'hourly_rate': 1.5,
            'overtime_rate': 2.25,
            'overtime_two_rate': 3,
            'commission': cls.commission.pk,
            'allowances': cls.allowance.pk,
            'deductions': cls.deduction.pk,
            'lunch_duration': '0:15:00',
            'pay_frequency': 2
        }

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        common_data.tests.test_models.create_test_common_entities(cls)

        
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

    def test_get__pay_grade_detail_page(self):
        resp = self.client.get(reverse('employees:pay-grade-detail', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)


    def test_post_update_pay_grade_page(self):
        resp = self.client.post(reverse('employees:update-pay-grade', kwargs={
            'pk': 1
        }), data=self.PAYGRADE_DATA)

        self.assertEqual(resp.status_code, 302)


class PaySlipPageTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'journals.json', 
        'employees.json', 'invoicing.json', 'payroll.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        create_test_employees_models(cls)
        common_data.tests.test_models.create_test_common_entities(cls)

        
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_pay_slips_list_page(self):
        resp = self.client.get(reverse('employees:list-pay-slips'))
        self.assertEqual(resp.status_code, 200)

        def test_get_employee_pay_slips_list_page(self):
            resp = self.client.get(reverse('employees:list-employee- pay-slips', kwargs={
                'pk': 1
            }))
            self.assertEqual(resp.status_code, 200)

    def test_get_pay_slip_detail_page(self):
        resp = self.client.get(reverse('employees:pay-slip-detail', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_pay_slip_basic_page(self):
        resp = self.client.get(reverse('employees:pay-slip-basic', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_payslip_basic_pdf_view(self):
        kwargs = {'pk': 1}
        req = RequestFactory().get(reverse('employees:basic-pay-slip-pdf', 
            kwargs=kwargs))
        resp = PayslipPDFView.as_view()(req, **kwargs)
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

    def test_payslip_pdf_view(self):
        kwargs = {'pk': 1}
        req = RequestFactory().get(reverse('employees:pay-slip-pdf', 
            kwargs=kwargs))
        resp = PayslipPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)

    def test_payslip_verify_status(self):
        settings = EmployeesSettings.objects.get(pk=1)
        settings.payroll_officer = self.officer
        settings.save()
        
        resp = self.client.get('/employees/pay-slip-verify-status/1')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Payslip.objects.get(pk=1).status, 'verified')

    def test_execute_payroll(self):
        settings = EmployeesSettings.objects.first()
        settings.payroll_officer = self.officer
        settings.save()

        prev_entry_count = JournalEntry.objects.all().count()
        self.slip.status = 'verified'
        self.slip.save()
        resp = self.client.get('/employees/execute-payroll')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(prev_entry_count != JournalEntry.objects.all().count())

    


class EmployeePageTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json']

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
                'pay_grade': cls.grade.pk,
                'leave_days': 0,
                'pin': 1000
                }

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        common_data.tests.test_models.create_test_common_entities(cls)


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
        obj = Employee.objects.create(
            first_name = 'Fi23rst',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            pay_grade = self.grade
        )
        resp = self.client.post('/employees/employee/create-user/' + str(obj.pk),
            data={
                'employee':  obj.pk,
                'username': 'name22',
                'password': 'password',
                'confirm_password': 'password'
            })
        
        self.assertEqual(resp.status_code, 302)
        obj.delete()

    def test_employees_create_user_page_post_with_error(self):
        
        resp = self.client.post('/employees/employee/create-user/1',
            data={
                'employee': 1,
                'username': 'name2',
                'password': 'passw0rd',
                'confirm_password': 'password'
            })
        #error has a 200 status code
        self.assertEqual(resp.status_code, 200)

    def test_employees_get_reset_password_page(self):
        resp = self.client.get('/employees/employee/user/reset-password/1')
        self.assertEqual(resp.status_code, 200)

    def test_employees_reset_password_page_post(self):
        su = User.objects.create_superuser('admin', 'test@email.com', 'password')
        resp = self.client.post('/employees/employee/user/reset-password/1',
            data={
                'employee': 1,
                'superuser': 'admin',
                'superuser_password': 'password',
                'new_user_password': 'new_password',
                'confirm_new_user_password': 'new_password'
            })
        self.assertEqual(resp.status_code, 302)

    def test_employees_delete_user_post(self):
        resp = self.client.get('/employees/employee/delete-user/1')
        self.assertEqual(resp.status_code, 302)

    def test_get_employee_payslips(self):
        resp = self.client.get('/employees/list-employee-pay-slips/1')
        self.assertEqual(resp.status_code, 200)
        

class BenefitsPageTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json']

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
        common_data.tests.test_models.create_test_common_entities(cls)


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
        self.assertEqual(resp.status_code, 200)

    def test_get_allowance_detail_page(self):
        resp = self.client.get(reverse('employees:allowance-details',
            kwargs={
                'pk': self.allowance.pk
            }))
        self.assertEqual(resp.status_code, 200)
        
    
    def test_get_allowance_list(self):
        resp = self.client.get(reverse('employees:allowances-list'))
        self.assertEqual(resp.status_code, 200)


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
    fixtures = ['common.json','accounts.json', 'employees.json']

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
        common_data.tests.test_models.create_test_common_entities(cls)


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
        self.assertEqual(resp.status_code, 200)

    def test_get_commission_rule_detail_page(self):
        resp = self.client.get(reverse('employees:commission-details',
            kwargs={
                'pk': self.commission.pk
            }))
        self.assertEqual(resp.status_code, 200)


    def test_get_commission_rule_list_page(self):
        resp = self.client.get(reverse('employees:commissions-list'))
        self.assertEqual(resp.status_code, 200)
        

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
    fixtures = ['common.json','accounts.json', 'employees.json', 'payroll.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        cls.DEDUCTION_DATA = {
                'name': 'Other Test Deduction',
                'deduction_method': 1,
                'fixed_amount': 10,
                'rate': 0,
                'account_paid_into': 5008,
                'employer_contribution':0,
                'liability_account': 2010
            }
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        common_data.tests.test_models.create_test_common_entities(cls)
        return super().setUpTestData()

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_deduction_page(self):
        resp = self.client.get(reverse('employees:create-deduction'))
        self.assertTrue(resp.status_code == 200)

    def test_get_deduction_page(self):
        resp = self.client.get(reverse('employees:deductions-list'))
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
        self.assertEqual(resp.status_code, 200)

    def test_get_deduction_detail_page(self):
        resp = self.client.get(reverse('employees:deduction-detail',
            kwargs={
                'pk': self.deduction.pk
            }))
        self.assertEqual(resp.status_code, 200)

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
        data['liability_account'] = Account.objects.get(pk=5008)
        
        Deduction.objects.create(**data)
        resp = self.client.post(reverse('employees:delete-deduction',
            kwargs={
                'pk': Deduction.objects.latest('pk').pk
            }))


class PayrollTaxViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        common_data.tests.test_models.create_test_common_entities(cls)


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
                'paid_by': 1,
                'brackets': urllib.parse.quote(json.dumps([{
                    'lower_limit': 0,
                    'upper_limit': 300,
                    'rate': 10,
                    'deduction': 0
                }])),
            })

        self.assertEqual(resp.status_code, 302)

    def test_get_payroll_tax_list_page(self):
        resp = self.client.get('/employees/payroll-tax-list')
        self.assertEqual(resp.status_code, 200)

    def test_payroll_tax_delete_page_get(self):
        other_prt = PayrollTax.objects.create(
            name="name",
            paid_by=0
        )
        resp = self.client.post('/employees/payroll-tax-delete/2')
        self.assertEqual(resp.status_code, 302)


class PayrollOfficerViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        common_data.tests.test_models.create_test_common_entities(cls)


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
        obj = Employee.objects.create(
            first_name = '23First',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            pay_grade = self.grade
        )
        resp = self.client.post('/employees/payroll-officer/create',
            data={
                'employee': obj.pk
            })
        self.assertEqual(resp.status_code, 302)
        obj.delete()

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
    fixtures = ['common.json','accounts.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        common_data.tests.test_models.create_test_common_entities(cls)
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
        self.assertTrue(True)
        data = {
                'status': 1,
                'notes': 'Note',
                'password': 'password',
                'authorized_by': self.officer.pk,
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
    fixtures = ['common.json','accounts.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        common_data.tests.test_models.create_test_common_entities(cls)
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
                        'date': '1',
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


class EmployeeWizardTests(TestCase):
    fixtures = ['common.json','accounts.json', 'journals.json', 'settings.json', 'employees.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(username="Testuser", email="admin@test.com", password="123")

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_employees_wizard(self):
        date_data = {
            'config_wizard-current_step': 0,
            '0-date': 5,
            '0-schedule': 1

        }

        grade_data = {
            '1-name': 'name',
            '1-monthly_leave_days': 1.5,
            '1-salary': 100,
            '1-pay_frequency': 2,
            '1-hourly_rate': 1.5,
            '1-overtime_rate': 2,
            '1-overtime_two_rate': 4,
            '1-lunch_duration': '0:15:00',
            'config_wizard-current_step': 1
        }

        employee_data = {
            '2-first_name': 'name',
            '2-last_name': 'last',
            '2-leave_days': 1,
            '2-pin': 2000,
            'config_wizard-current_step': 2
        }

        payroll_officer_data = {
            '3-employee': 1,
            'config_wizard-current_step': 3
        }

        settings_data = {
            '4-payroll_account': 1000,
            '4-payroll_counter': 10,
            'config_wizard-current_step': 4
        }

        data_list = [date_data, grade_data, employee_data, 
            payroll_officer_data, settings_data]

        for step, data in enumerate(data_list, 1):
            resp = self.client.post(reverse('employees:config-wizard'), 
                data=data)

            if step == len(data_list):
                self.assertEqual(resp.status_code, 302)
            else:

                self.assertEqual(resp.status_code, 200)


class PayrollDateViewTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'settings.json', 'journals.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('TestUser', 'admin@mail.com', '123')

        cls.date = PayrollDate.objects.create(
            date=1
        )
        create_test_employees_models(cls)
       

    def setUp(self):
        self.client.login(username='TestUser', password='123')

    def test_get_payroll_date_create_view(self):
        resp = self.client.get(reverse('employees:payroll-date-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_payroll_date_create_view(self):
        resp = self.client.post(reverse('employees:payroll-date-create'), data={
            'date': 2,
            'schedule': 1
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_payroll_date_update_view(self):
        resp = self.client.get(reverse('employees:payroll-date-update', kwargs={
            'pk': self.date.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_payroll_date_update_view(self):
        resp = self.client.post(reverse('employees:payroll-date-update',
            kwargs={'pk': 1}), data={
            'date': 2,
            'schedule': 1
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_payroll_date_delete_view(self):
        resp = self.client.get(reverse('employees:payroll-date-delete', kwargs={
            'pk': self.date.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_payroll_date_delete_view(self):
        obj = PayrollDate.objects.create(date=4)
        resp = self.client.post(reverse('employees:payroll-date-delete', kwargs={
            'pk': obj.pk
        }))
        self.assertEqual(resp.status_code, 302)


    def test_get_payroll_date_detail_view(self):
        resp = self.client.get(reverse('employees:payroll-date-detail', kwargs={
            'pk': self.date.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_payroll_date_list_view(self):
        resp = self.client.get(reverse('employees:payroll-date-list'))
        self.assertEqual(resp.status_code, 200)


class DepartmentViewTests(TestCase):
    fixtures = ['common.json','accounts.json','journals.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        User.objects.create_superuser('Testuser', 'admin@mail.com', '123')
        cls.dept = Department.objects.create(name='dept')

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_department_create_view(self):
        resp = self.client.get(reverse('employees:department-create'))
        self.assertEqual(resp.status_code, 200)

    def test_get_department_list_view(self):
        resp = self.client.get(reverse('employees:department-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_department_update_view(self):
        resp = self.client.get(reverse('employees:department-update', kwargs={
            'pk':self.dept.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_department_detail_view(self):
        resp = self.client.get(reverse('employees:department-detail', kwargs={
            'pk': self.dept.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_department_create_view(self):
        resp = self.client.post(reverse('employees:department-create'), data={
            'name': 'other dept',
            'manager': self.employee.pk,
            'employees': [1]
        })

        self.assertEqual(resp.status_code, 302)

    def test_post_department_update_view(self):
        resp = self.client.post(reverse('employees:department-update', kwargs={
            'pk': 1
        }), data={
            'name': 'other dept',
            'manager': self.employee.pk,
            'employees': [1]

        })

        self.assertEqual(resp.status_code, 302)

class EmployeesReportViewTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'journals.json', 
        'employees.json', 'payroll.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        User.objects.create_superuser('Testuser', 'admin@mail.com', '123')


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_employee_attendance_report(self):
        resp = self.client.get(reverse('employees:employee-attendance'))
        self.assertEqual(resp.status_code, 200)

    def test_employee_attendance_pdf(self):
        req = RequestFactory().get(reverse('employees:employee-attendance-pdf'))
        resp = EmployeeAttendanceReportPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_leave_report(self):
        resp = self.client.get(reverse('employees:leave-report'))
        self.assertEqual(resp.status_code, 200)

    def test_leave_report_pdf(self):
        req = RequestFactory().get(reverse('employees:leave-report-pdf'))
        resp = LeaveReportPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_payroll_report_form(self):
        resp = self.client.get(reverse('employees:payroll-report-form'))
        self.assertEqual(resp.status_code, 200)

    def test_payroll_report(self):
        resp = self.client.get(reverse('employees:payroll-report'), data={
            'default_periods': 4
        })
        self.assertEqual(resp.status_code, 200)

    def test_payroll_report_pdf(self):
        kwargs = {
            'start': (datetime.date.today() \
                - datetime.timedelta(days=365)).strftime("%d %B %Y"),
            'end': datetime.date.today().strftime('%d %B %Y')
        }
        req = RequestFactory().get(reverse('employees:payroll-report-pdf', 
            kwargs=kwargs))

        resp = PayrollPDFReport.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)