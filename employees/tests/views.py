import json 
import os 
import urllib
import datetime
import decimal

from django.test import TestCase, Client
from django.shortcuts import reverse

from employees.models import *
from .models import create_employees_models
from latrom import settings
from common_data.tests import create_test_user

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()


class GenericPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(GenericPageTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

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
        EmployeesSettings.objects.create(
            payroll_date_one = 1,
            payroll_date_two = 14,
            payroll_date_three = 21,
            payroll_date_four = 28,
            payroll_cycle = 'weekly',
            require_verification_before_posting_payslips = True,
            salary_follows_profits = True
        )
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
        super(PayGradePageTests, cls).setUpClass()
        create_test_user(cls)
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
            'deductions': cls.deduction.pk
        }

    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

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
    @classmethod
    def setUpClass(cls):
        super(PaySlipPageTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

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

    

class EmployeePageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(EmployeePageTests, cls).setUpClass()
        create_test_user(cls)
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
                'leave_days': 0
                }

    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

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


class BenefitsPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BenefitsPageTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()
        cls.ALLOWANCE_DATA = {
                'name': 'Other Test Allowance',
                'amount': 100
            }
        
    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

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
        super(CommissionPageTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()
        cls.COMMISSION_DATA = {
                'name': 'Test Rule',
                'min_sales': 100,
                'rate': 10
            }
        
    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

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
    @classmethod
    def setUpClass(cls):
        super(DeductionPageTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()
        cls.DEDUCTION_DATA = {
                'name': 'Other Test Deduction',
                'method': 1,
                'trigger':1,
                'amount': 10,
                'rate': 0
            }
        
    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_deduction_page(self):
        resp = self.client.get(reverse('employees:create-deduction'))
        self.assertTrue(resp.status_code == 200)

    def test_post_deduction_page(self):
        resp = self.client.post(reverse('employees:create-deduction'),
            data=self.DEDUCTION_DATA)
        self.assertTrue(resp.status_code == 302)
        
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

        self.assertTrue(resp.status_code == 302)

    def test_get_deduction_delete(self):
        resp = self.client.get(reverse('employees:delete-deduction',
            kwargs={
                'pk': self.deduction.pk
            }))

    def test_post_deduction_delete(self):
        Deduction.objects.create(**self.DEDUCTION_DATA)
        resp = self.client.post(reverse('employees:delete-deduction',
            kwargs={
                'pk': Deduction.objects.latest('pk').pk
            }))
