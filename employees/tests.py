# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from django.shortcuts import reverse
import json 
import os 
import urllib
from models import *
import datetime
import decimal
from latrom import settings
from common_data.tests import create_test_user

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()

def create_employees_models(cls):
    cls.allowance = Allowance.objects.create(
            name='Model Test Allowance',
            amount=50
        )
    cls.deduction = Deduction.objects.create(
            name='Model test deduction',
            method=0,
            rate=10,
        )
    cls.commission=CommissionRule.objects.create(
            name='Model Test Commission',
            min_sales = 5000,
            rate=15
        )
    cls.grade = PayGrade.objects.create(
            name='Model Test Paygrade',
            monthly_salary=300,
            monthly_leave_days=1.5,
            hourly_rate=2,
            overtime_rate=3,
            overtime_two_rate=4,
            commission= cls.commission,
        )
    cls.grade.allowances.add(cls.allowance)
    cls.grade.deductions.add(cls.deduction)
    cls.grade.save()

    cls.employee = Employee.objects.create(
            first_name = 'First',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            hire_date=TODAY,
            title='test role',
            pay_grade = cls.grade
        )

    cls.slip = Payslip.objects.create(
        start_period=TODAY,
            end_period=TODAY + datetime.timedelta(days=30),
            employee=cls.employee,
            normal_hours=0,
            overtime_one_hours=20,
            overtime_two_hours=0,
            pay_roll_id = 1
    )

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)

    def test_create_deduction(self):
        Deduction.objects.create(
            name='test deduction',
            method=0,
            rate=10,
        )
        deduction = Deduction.objects.get(name='test deduction')
        
        self.assertTrue(isinstance(
            deduction, 
            Deduction))

    def test_create_allowance(self):
        Allowance.objects.create(
            name='Test Allowance',
            amount=50
        )

        self.assertTrue(isinstance(
            Allowance.objects.get(name='Test Allowance'), 
            Allowance))

    def test_create_commission_rule(self):
        CommissionRule.objects.create(
            name='Test Commission',
            min_sales = 5000,
            rate=15
        )

        self.assertTrue(isinstance(
            CommissionRule.objects.get(name='Test Commission'), 
            CommissionRule))

    def test_create_pay_grade(self):
        grade = PayGrade.objects.create(
            name='Test Paygrade',
            monthly_salary=300,
            monthly_leave_days=1.5,
            hourly_rate=2,
            overtime_rate=3,
            overtime_two_rate=4,
            commission= self.commission,
        )
        grade.allowances.add(self.allowance)
        grade.deductions.add(self.deduction)
        grade.save()

        paygrade = PayGrade.objects.get(name='Test Paygrade')
        self.assertTrue(isinstance(
            paygrade, PayGrade))
        self.assertEqual(paygrade.total_allowances, 50)


    def test_create_payslip(self):
        Payslip.objects.create(
            start_period=TODAY,
            end_period=TODAY + datetime.timedelta(days=30),
            employee=self.employee,
            normal_hours=173,
            overtime_one_hours=20,
            overtime_two_hours=0,
            pay_roll_id = 1
        )

        slip = Payslip.objects.get(normal_hours=173)
        self.assertTrue(isinstance(
            slip, 
            Payslip))

        # not fully implemented commission

        self.assertEqual(slip.normal_pay, 346)
        self.assertEqual(slip.overtime_one_pay, 60)
        self.assertEqual(slip.overtime_two_pay, 0)
        self.assertEqual(slip.gross_pay, 756)
        self.assertAlmostEqual(slip.PAYE, 91.2)
        self.assertEqual(slip.net_pay, 589.2)

    def test_create_employee(self):
        Employee.objects.create(
            first_name = 'First',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '12345678',
            hire_date=TODAY,
            title='role test',
            pay_grade = self.grade
        )

        self.assertTrue(isinstance(
            Employee.objects.get(phone='12345678'), 
            Employee))

class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        create_employees_models(cls)
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

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_employee_form(self):
        resp = self.client.get(reverse('employees:create-employee'))
        self.assertTrue(resp.status_code==200)

    def test_post_employee_form_and_delete(self):
        resp = self.client.post(reverse('employees:create-employee'),
            data=self.EMPLOYEE_DATA)
        self.assertTrue(resp.status_code == 302)
        
        emp = Employee.objects.latest('pk')
        
        resp = self.client.post(reverse('employees:employee-delete',
            kwargs={
                'pk': emp.pk
            }))
        self.assertTrue(resp.status_code == 302)

    def test_post_employee_update(self):
        resp = self.client.post(reverse('employees:employee-update',
            kwargs={
                'pk': self.employee.pk
            }), data=self.EMPLOYEE_DATA)

        self.assertTrue(resp.status_code == 302)

    def test_get_employee_list(self):
        resp = self.client.get(reverse('employees:list-employees'))
        self.assertTrue(resp.status_code==200)

    def test_get_employee_update_form(self):
        resp = self.client.get(reverse('employees:employee-update',
             kwargs={'pk': self.employee.pk}))
        self.assertTrue(resp.status_code==200)

    def test_get_employee_detail_form(self):
        resp = self.client.get(reverse('employees:employee-detail', 
            kwargs={'pk': self.employee.pk}))
        self.assertTrue(resp.status_code==200)

    def test_get_employee_delete_form(self):
        resp = self.client.get(reverse('employees:employee-delete', 
            kwargs={'pk': self.employee.pk}))
        self.assertTrue(resp.status_code==200)

    def test_post_employee_delete_form(self):

        resp = self.client.post(reverse('employees:employee-delete', 
            kwargs={
                'pk': Employee.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code==302)


    def test_get_allowance_form(self):
        resp = self.client.get(reverse('employees:create-allowance'))
        self.assertTrue(resp.status_code == 200)

    def test_post_allowance_form_and_delete(self):
        resp = self.client.post(reverse('employees:create-allowance'),
            data={
                'name': 'Other Test Allowance',
                'amount': 100
            })
        self.assertTrue(resp.status_code == 302)
        all = Allowance.objects.latest('pk')
        resp = self.client.post(reverse('employees:delete-allowance',
            kwargs={
                'pk': all.pk
            }))

        self.assertTrue(resp.status_code==302)

    def test_post_allowance_update_form(self):
        resp = self.client.post(reverse('employees:update-allowance',
            kwargs={
                'pk': self.allowance.pk
        }),
            data={
                'name': 'Other Test Allowance',
                'amount': 100
            })
        self.assertTrue(resp.status_code == 302)

    def test_get_allowance_update(self):
        resp = self.client.get(reverse('employees:update-allowance',
            kwargs={
                'pk': self.allowance.pk
            }))

    def test_get_allowance_delete(self):
        resp = self.client.get(reverse('employees:delete-allowance',
            kwargs={
                'pk': self.allowance.pk
            }))

    def test_post_allowance_delete(self):
        resp = self.client.post(reverse('employees:delete-allowance',
            kwargs={
                'pk': Allowance.objects.latest('pk').pk
            }))

    def test_get_util_list_page(self):
        resp = self.client.get(reverse('employees:util-list'))
        self.assertTrue(resp.status_code == 200)

    
    def test_get_commission_form(self):
        resp = self.client.get(reverse('employees:create-commission'))
        self.assertTrue(resp.status_code == 200)

    def test_post_commission_form_and_delete(self):
        resp = self.client.post(reverse('employees:create-commission'),
            data={
                'name': 'Test Rule',
                'min_sales': 100,
                'rate': 10
            })
        self.assertTrue(resp.status_code == 302)

        com = CommissionRule.objects.latest('pk')
        resp = self.client.post(reverse('employees:delete-commission',
            kwargs={
                'pk': com.pk
            }))
        self.assertTrue(resp.status_code== 302)

    def test_get_commission_update(self):
        resp = self.client.get(reverse('employees:update-commission',
            kwargs={
                'pk': self.commission.pk
            }))

    def test_post_commission_update(self):
        resp = self.client.post(reverse('employees:update-commission',
            kwargs={
                'pk': self.commission.pk
            }), data={
                'name': 'Changed test name',
                'min_sales': 10,
                'rate': 100
            })

        self.assertTrue(resp.status_code==302)

    def test_get_commission_delete(self):
        resp = self.client.get(reverse('employees:delete-commission',
            kwargs={
                'pk': self.commission.pk
            }))

    def test_post_commission_delete(self):
        resp = self.client.post(reverse('employees:delete-commission',
            kwargs={
                'pk': CommissionRule.objects.latest('pk').pk
            }))

    def test_get_deduction_form(self):
        resp = self.client.get(reverse('employees:create-deduction'))
        self.assertTrue(resp.status_code == 200)

    def test_post_deduction_form_and_delete(self):
        resp = self.client.post(reverse('employees:create-deduction'),
            data={
                'name': 'Other Test Deduction',
                'method': 0,
                'rate': 10,
                'trigger':1,
                'amount': 0,
            })
        self.assertTrue(resp.status_code == 302)
        
        ded = Deduction.objects.latest('pk')
        resp = self.client.post(reverse('employees:delete-deduction',
            kwargs={
                'pk': ded.pk
            }))

        self.assertTrue(resp.status_code == 302)

    def test_get_deduction_update(self):
        resp = self.client.get(reverse('employees:update-deduction',
            kwargs={
                'pk': self.deduction.pk
            }))

    def test_post_deduction_update(self):
        resp = self.client.post(reverse('employees:update-deduction',
            kwargs={
                'pk': self.deduction.pk
            }), data={
                'name': 'Other Test Deduction',
                'method': 1,
                'trigger':1,
                'amount': 10,
                'rate': 0
            })

        self.assertTrue(resp.status_code == 302)

    def test_get_deduction_delete(self):
        resp = self.client.get(reverse('employees:delete-deduction',
            kwargs={
                'pk': self.deduction.pk
            }))

    def test_post_deduction_delete(self):
        resp = self.client.post(reverse('employees:delete-deduction',
            kwargs={
                'pk': Deduction.objects.latest('pk').pk
            }))

    def test_get_payslips_page(self):
        resp = self.client.get(reverse('employees:list-pay-slips'))
        self.assertTrue(resp.status_code == 200)
    
    def test_get_payslip_detail(self):
        resp = self.client.get(reverse('employees:pay-slip-detail',
            kwargs={
                'pk': self.slip.pk
            }))
        self.assertTrue(resp.status_code == 200)

    #PAYROLL

    def test_get_employees_page(self):
        resp = self.client.get(reverse('employees:dashboard'))
        self.assertTrue(resp.status_code == 200)

    #PAYGRADE
    
    def test_get_pay_grade_form(self):
        resp = self.client.get(reverse('employees:create-pay-grade'))
        self.assertTrue(resp.status_code == 200)

    def test_post_pay_grade_form(self):
        resp = self.client.post(reverse('employees:create-pay-grade'),
        data=self.PAYGRADE_DATA)
        self.assertTrue(resp.status_code == 302)
        # no delete page for pay grades 

    def test_get_pay_grade_list(self):
        resp = self.client.get(reverse('employees:list-pay-grades'))
        self.assertTrue(resp.status_code == 200)

    def test_get_update_pay_grade_form(self):
        resp = self.client.get(reverse('employees:update-pay-grade',
            kwargs={
                'pk': self.grade.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_update_pay_grade_form(self):
        resp = self.client.post(reverse('employees:update-pay-grade',
            kwargs={
                'pk': self.grade.pk
            }), data=self.PAYGRADE_DATA)

        self.assertTrue(resp.status_code == 302)