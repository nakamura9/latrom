import json 
import os 
import urllib
import datetime
import decimal

from django.test import TestCase, Client
from django.shortcuts import reverse

from employees.models import *
from latrom import settings
from common_data.tests import create_test_user

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()

from employees.models import *



def create_test_employees_models(cls):
    cls.allowance = Allowance.objects.create(
            name='Model Test Allowance',
            amount=50
        )
    cls.deduction = Deduction.objects.create(
            name='Model test deduction',
            method=1,
            amount=10,
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
    cls.prt = PayrollTax.objects.create(name='Test Tax', paid_by=0)
    cls.tb = TaxBracket.objects.create(
            payroll_tax=cls.prt,
            lower_boundary=0,
            upper_boundary=1000,
            rate=10.0,
            deduction=0)
    cls.grade.payroll_taxes.add(cls.prt)
    cls.grade.save()

    cls.slip = Payslip.objects.create(
        start_period=TODAY,
            end_period=TODAY + datetime.timedelta(days=30),
            employee=cls.employee,
            normal_hours=100,
            overtime_one_hours=0,
            overtime_two_hours=0,
            pay_roll_id = 1
    )

class CommonModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)


    def test_create_employee_settings(self):
        obj = EmployeesSettings.objects.create(
            payroll_date_one = 1,
            payroll_date_two = 14,
            payroll_date_three = 21,
            payroll_date_four = 28,
            payroll_cycle = 'weekly',
            require_verification_before_posting_payslips = True,
            salary_follows_profits = True
            #automate_payroll_for
        )
        self.assertIsInstance(obj, EmployeesSettings)


class EmployeeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def test_create_employee(self):
        obj = Employee.objects.create(
            first_name = 'First',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            hire_date=TODAY,
            title='test role',
            pay_grade = self.grade
        )
        self.assertIsInstance(obj, Employee)

    def test_get_payslips(self):
        slips = self.employee._payslips_YTD
        self.assertTrue(slips.count() == 1)

    def test_deductions(self):
        deducted = self.employee.deductions_YTD
        self.assertEqual(deducted, 65)

    def test_earnings(self):
        earnings = self.employee.earnings_YTD
        self.assertEqual(earnings, 550)


    def test_roles(self):
        # for users logged in to the application
        self.assertFalse(self.employee.is_sales_rep)
        self.assertFalse(self.employee.is_inventory_controller)
        self.assertFalse(self.employee.is_bookkeeper)
        

class AllowanceModelTest(TestCase):
    def test_create_allowance(self):
        allowance = Allowance.objects.create(
            name='Model Test Allowance',
            amount=50
        )
        self.assertIsInstance(allowance, Allowance)

class DeductionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def test_create_fixed_deduction(self):
        obj = Deduction.objects.create(
            name='test deduction',
            method=1,
            amount=10
            )
        self.assertIsInstance(obj, Deduction)

    def test_create_rated_deduction(self):
        obj = Deduction.objects.create(
            name='test deduction',
            method=0,
            rate=10)
        self.assertIsInstance(obj, Deduction)


    def test_deduction_from_payslip_if_fixed(self):
        fixed_deduction = Deduction.objects.create(
            name='test fixed deduction',
            method=1,
            amount=10
            )
        deducted = fixed_deduction.deduct(self.slip)
        self.assertEqual(deducted, fixed_deduction.amount)


    def test_deduction_from_payslip_if_rated(self):
        rated_deduction = Deduction.objects.create(
            name='test rated deduction',
            method=0,
            trigger=0,
            rate=10
            )
        deducted = rated_deduction.deduct(self.slip)
        self.assertEqual(deducted, (0.1 * self.slip.gross_pay))


class CommissionRuleModelTest(TestCase):
    def test_create_commission_rule(self):
        obj = CommissionRule.objects.create(
            name='Test Rule',
            min_sales= 1000,
            rate=10
        )
        self.assertIsInstance(obj, CommissionRule)


class PayGradeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
    
    def test_create_pay_grade(self):
        obj = PayGrade.objects.create(
            name='Test Paygrade',
            monthly_salary=300,
            monthly_leave_days=1.5,
            hourly_rate=2,
            overtime_rate=3,
            overtime_two_rate=4,
            commission= self.commission,
        )

        self.assertIsInstance(obj, PayGrade)

    def test_total_and_taxable_allowances(self):
        self.grade.allowances.clear()
        allowance = Allowance.objects.create(
            name='test allowance',
            amount=100,
            taxable=True
        )
        untaxable_allowance = Allowance.objects.create(
            name='untaxable test allowance',
            amount=50,
            taxable=False
        )
        self.grade.allowances.add(allowance)
        self.grade.allowances.add(untaxable_allowance)
        self.grade.save()
        self.assertEqual(self.grade.total_allowances, 150)
        self.assertEqual(self.grade.tax_free_benefits, 50)

class PaySlipModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def test_create_pay_slip(self):
        obj = Payslip.objects.create(
            start_period=TODAY,
            end_period=TODAY + datetime.timedelta(days=30),
            employee=self.employee,
            normal_hours=173,
            overtime_one_hours=20,
            overtime_two_hours=0,
            pay_roll_id = 1
        )
        self.assertIsInstance(obj, Payslip)

    def test_commission_pay(self):
        # create per test commission 
        commission = CommissionRule.objects.create(
            name = 'Test commission', 
            min_sales = 0,
            rate = 10
        )
        self.grade.commission = commission
        self.grade.save()

        #because there is no sales representative
        self.assertEqual(self.slip.commission_pay, 0)

    def test_pay_schemes(self):
        self.slip.normal_hours = 100
        self.slip.overtime_one_hours = 10
        self.slip.overtime_two_hours = 5
        self.slip.save()
        self.assertEqual(self.slip.normal_pay, 200)
        self.assertEqual(self.slip.overtime_one_pay, 30)
        self.assertEqual(self.slip.overtime_two_pay, 20)
        self.assertEqual(self.slip.overtime_pay, 50)

    def test_gross_pay(self):
        self.assertEqual(self.slip.gross_pay, 550)

    def test_taxable_gross_pay(self):
        self.assertEqual(self.slip.taxable_gross_pay, 600)

    def test_deductions(self):
        self.assertEqual(self.slip._deductions, 10)

    def test_payroll_taxes(self):
        self.assertEqual(self.slip.total_payroll_taxes, 60)

    def test_total_deductions(self):
        self.assertEqual(self.slip.total_deductions, 70)

    def test_net_pay(self):
        self.assertEqual(self.slip.net_pay, 485)

class TaxBracketModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def test_create_payroll_tax(self):
        obj = PayrollTax.objects.create(
            name='test payroll tax',
            paid_by=0)

        self.assertIsInstance(obj, PayrollTax)

    def test_create_tax_bracket(self):
        obj = TaxBracket.objects.create(
            payroll_tax=self.prt,
            lower_boundary=300,
            upper_boundary=1000,
            rate= 20,
            deduction=25)

        self.assertIsInstance(obj, TaxBracket)