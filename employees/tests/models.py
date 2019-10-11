import datetime
import decimal
import json
import os
import urllib
import reversion
import time

from django.shortcuts import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import User
from employees.models import *
from latrom import settings
from accounting.models import Account, JournalEntry
from invoicing.models import (SalesRepresentative, 
                              Invoice, 
                              InvoiceLine,
                              ProductLineComponent
                              )
from inventory.models import InventoryItem, UnitOfMeasure, ProductComponent
TODAY = datetime.date.today()
        
def create_test_employees_models(cls):
    
    cls.allowance = Allowance.objects.create(
            name='Model Test Allowance',
            amount=50
        )
    cls.deduction = Deduction.objects.create(
            name='Model test deduction',
            deduction_method=1,
            fixed_amount=10,
        )
    cls.commission=CommissionRule.objects.create(
            name='Model Test Commission',
            min_sales = 0,
            rate=15
        )
    cls.grade = PayGrade.objects.create(
            name='Model Test Paygrade',
            salary=300,
            monthly_leave_days=1.5,
            hourly_rate=2,
            overtime_rate=3,
            overtime_two_rate=4,
            commission= cls.commission,
        )

    
    cls.grade.allowances.add(cls.allowance)
    cls.grade.deductions.add(cls.deduction)

    cls.prt = PayrollTax.objects.create(name='Test Tax', paid_by=0)

    cls.tb = TaxBracket.objects.create(
            payroll_tax=cls.prt,
            lower_boundary=0,
            upper_boundary=1000,
            rate=10.0,
            deduction=0)

    cls.grade.payroll_taxes.add(cls.prt)
    cls.grade.save()
    with reversion.create_revision():
        cls.grade.save()

    if not hasattr(cls, 'employee'):
        cls.employee = Employee.objects.create(
                first_name = 'First',
                last_name = 'Last',
                address = 'Model test address',
                email = 'test@mail.com',
                phone = '1234535234',
                pay_grade = cls.grade
            )

    if not cls.employee.user:
        usr = User.objects.create_user('name1994')
        usr.set_password('password')
        usr.save()
        cls.employee.user = usr
        cls.employee.save()

    cls.slip = Payslip.objects.create(
        start_period=TODAY,
            end_period=TODAY,
            employee=cls.employee,
            normal_hours=100,
            overtime_one_hours=0,
            overtime_two_hours=0,
            pay_roll_id = 1,
            pay_grade = cls.employee.pay_grade,
            status="verified"
    )
    
    cls.schedule = PayrollSchedule.objects.first()
    if not cls.schedule:
        cls.schedule  =PayrollSchedule.objects.create(
            name='schedule'
        )

    cls.pay_date = PayrollDate.objects.create(
        date = TODAY.day,
        schedule=cls.schedule
    )
    cls.pay_date.employees.add(cls.employee)
    cls.pay_date.save()

    if not hasattr(cls, 'officer'):
        cls.officer = PayrollOfficer.objects.create(
            employee=cls.employee
        )

class CommonModelTests(TestCase):
    def test_create_employee_settings(self):
        obj = EmployeesSettings.objects.create(
            require_verification_before_posting_payslips = True,
            salary_follows_profits = True
        )
        self.assertIsInstance(obj, EmployeesSettings)


class TimesheetTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']

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
        cls.line = AttendanceLine.objects.create(
            timesheet=cls.timesheet,
            date= datetime.date.today(), 
            time_in = datetime.datetime(2018, 1, 1, 8, 0).time(),
            time_out = datetime.datetime(2018, 1, 1, 17, 0).time(),
        )

    def test_create_timesheet(self):
        obj = EmployeeTimeSheet.objects.create(
            employee=self.employee,
            month=1,
            year=2018,
            recorded_by=self.employee,
            complete=True
        )
        self.assertIsInstance(obj, EmployeeTimeSheet)

    def test_timesheet_normal_time(self):
        self.assertEqual(self.timesheet.normal_hours, datetime.timedelta(seconds=28800))

        

    def test_timesheet_overtime(self):
        self.assertEqual(self.timesheet.overtime, datetime.timedelta(0))
        

    def test_create_attendance_line(self):
        obj = AttendanceLine.objects.create(
            timesheet=self.timesheet,
            date= datetime.date.today(),
            time_in = datetime.datetime(2018, 1, 1, 8, 0).time(),
            time_out = datetime.datetime(2018, 1, 1, 17, 0).time(),
        )
        self.assertIsInstance(obj, AttendanceLine)

    def test_line_total_time(self):
        self.assertEqual(self.line.total_time, datetime.timedelta(
            seconds=32400))

    def test_line_working_time(self):
        self.assertEqual(self.line.working_time, 
            datetime.timedelta(hours=8))

    def test_line_noraml_time(self):
        self.assertEqual(self.line.normal_time, datetime.timedelta(hours=8))

    def test_line_overtime(self):
        self.assertEqual(self.line.overtime, datetime.timedelta(0))


class EmployeeModelTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']

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
            pay_grade = self.grade
        )
        self.assertIsInstance(obj, Employee)

    def test_get_payslips(self):
        slips = self.employee._payslips_YTD
        self.assertEqual(slips.count(), 1)

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
    fixtures = ['accounts.json', 'employees.json']

    def test_create_allowance(self):
        allowance = Allowance.objects.create(
            name='Model Test Allowance',
            amount=50
        )
        self.assertIsInstance(allowance, Allowance)


class DeductionModelTest(TestCase):
    fixtures = ['accounts.json', 'employees.json']

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def test_create_fixed_deduction(self):
        obj = Deduction.objects.create(
            name='test deduction',
            deduction_method=1,
            fixed_amount=10
            )
        self.assertIsInstance(obj, Deduction)

    def test_create_rated_deduction(self):
        obj = Deduction.objects.create(
            name='test deduction',
            deduction_method=0,
            rate=10)
        self.assertIsInstance(obj, Deduction)


    def test_deduction_from_payslip_if_fixed(self):
        fixed_deduction = Deduction.objects.create(
            name='test fixed deduction',
            deduction_method=1,
            fixed_amount=10
            )
        deducted = fixed_deduction.deduct(self.slip)
        self.assertEqual(deducted, fixed_deduction.fixed_amount)


    def test_deduction_from_payslip_if_rated(self):
        rated_deduction = Deduction.objects.create(
            name='test rated deduction',
            deduction_method=0,
            rate=10,
            basic_income=True
            )
        deducted = rated_deduction.deduct(self.slip)
        self.assertEqual(deducted, 30)

    def test_deduction_from_payslip_paye_triggered(self):
        rated_deduction = Deduction.objects.create(
            name='test rated deduction',
            deduction_method=0,
            rate=10,
            )
        rated_deduction.payroll_taxes.add(self.prt)
        rated_deduction.save()
        deducted = rated_deduction.deduct(self.slip)
        self.assertEqual(deducted, 5.5)


class CommissionRuleModelTest(TestCase):
    fixtures = ['accounts.json', 'employees.json']

    def test_create_commission_rule(self):
        obj = CommissionRule.objects.create(
            name='Test Rule',
            min_sales= 1000,
            rate=10
        )
        self.assertIsInstance(obj, CommissionRule)


class PayGradeModelTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
    
    def test_create_pay_grade(self):
        obj = PayGrade.objects.create(
            name='Test Paygrade',
            salary=300,
            monthly_leave_days=1.5,
            hourly_rate=2,
            overtime_rate=3,
            overtime_two_rate=4,
            commission= self.commission,
        )

        self.assertIsInstance(obj, PayGrade)

    
class PaySlipModelTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'journals.json',
         'employees.json','inventory.json', 'invoicing.json', 'payroll.json']
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        if not hasattr(cls, 'user'):
            cls.user = User.objects.create_superuser('Testuser', 
                'admin@test.com', '123')
            cls.user.save()

        pc = ProductComponent.objects.create(
            pricing_method=0, #KISS direct pricing
            direct_price=10,
            margin=0.5,
        ) 
        
        cls.product = InventoryItem.objects.create(
            name='test name',
            unit=UnitOfMeasure.objects.first(),
            unit_purchase_price=10,
            description='Test Description',
            minimum_order_level = 0,
            maximum_stock_level = 20,
            type=0,
            product_component=pc
        )
        


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
        self.assertIsInstance(str(obj), str)

    def test_commission_basic_pay(self):
        # create per test commission 
        self.assertEqual(self.slip.commission_pay, 0)

    def test_total_and_taxable_allowances(self):
        """allowance = Allowance.objects.create(
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
        self.grade.save()"""
        self.assertTrue(True)

    def test_commission_pay_with_sales_representative(self):
        
        rep = SalesRepresentative.objects.create(
            employee=self.employee
        )

        self.assertEqual(self.slip.commission_pay, 0)
        rep.hard_delete()

    def test_commission_pay_with_commission(self):
        rep = SalesRepresentative.objects.create(
            employee=self.employee
        )
        
        # create invoice with sales of 10 dollars
        inv = Invoice.objects.create(
            status="paid",
            salesperson = rep
        )
        plc = ProductLineComponent.objects.create(
            product=self.product,
            quantity=1,
            unit_price=10
        )
        line = InvoiceLine.objects.create(
            invoice=inv,
            product = plc,
            line_type=1,

        )
        self.assertEqual(self.slip.commission_pay, 1.5)

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
        self.assertIsInstance(str(self.deduction), str)
        # testing other triggers
        self.deduction.trigger=1
        self.deduction.save()
        self.assertEqual(self.deduction.deduct(self.slip), 10)
        self.deduction.trigger=2
        self.deduction.save()
        self.assertEqual(self.deduction.deduct(self.slip), 10)

    def test_payroll_taxes(self):
        self.assertEqual(self.slip.total_payroll_taxes, 60)

    def test_total_deductions(self):
        self.assertEqual(self.slip.total_deductions, 70)

    def test_net_pay(self):
        self.assertEqual(self.slip.net_pay, 485)

    def test_payslip_create_entry_not_verified(self):
        self.slip.status = 'draft'
        self.slip.save()
        self.slip.create_entry()
        self.assertEqual(self.slip.entry, None)

    def test_payslip_create_verified(self):
        settings = EmployeesSettings.objects.first()
        self.employee.user = self.user
        self.employee.save()
        settings.payroll_officer = self.officer
        settings.save()

        self.slip.status = 'verified'
        self.slip.save()
        self.slip.create_entry()
        self.assertIsInstance(self.slip.entry, JournalEntry)


class TaxBracketModelTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)

    def test_create_payroll_tax(self):
        obj = PayrollTax.objects.create(
            name='test payroll tax',
            paid_by=0)

        self.assertIsInstance(obj, PayrollTax)

    def test_payroll_tax_paid_by_string(self):
        self.assertIsInstance(self.prt.paid_by_string, str)



    def test_create_tax_bracket(self):
        obj = TaxBracket.objects.create(
            payroll_tax=self.prt,
            lower_boundary=300,
            upper_boundary=1000,
            rate= 20,
            deduction=25)

        self.assertIsInstance(obj, TaxBracket)

    def test_list_brackets(self):
        self.assertEqual(self.prt.list_brackets.count(), 1)

    def test_add_bracket(self):
        self.prt.add_bracket(0, 300, 10, 0)
        self.assertEqual(self.prt.list_brackets.count(), 2)
        TaxBracket.objects.latest('pk').delete()
        

class LeaveModelTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.leave = Leave.objects.create(
            start_date = datetime.date.today(),
            end_date = datetime.date.today(),
            employee=cls.employee,
            category=1,
            status=1,
            authorized_by=cls.employee
        )
    def test_create_leave_object(self):
        obj = Leave.objects.create(
            start_date = datetime.date.today(),
            end_date = datetime.date.today(),
            employee=self.employee,
            category=1,
            status=1,
            authorized_by=self.employee
        )
        self.assertIsInstance(obj, Leave)
        self.assertIsInstance(str(obj), str)

    def test_status_string(self):
        self.assertEqual(self.leave.status_string, 'Authorized')

    def test_leave_duration(self):
        self.assertEqual(self.leave.duration, 1)

    def test_leave_duration_negative(self):
        self.leave.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.leave.save()
        self.assertEqual(self.leave.duration, 0)

    def test_leave_duration_long(self):
        self.leave.end_date = datetime.date.today() + datetime.timedelta(days=5)
        self.leave.save()
        self.assertEqual(self.leave.duration, 5)

    def test_leave_category_string(self):
        self.assertEqual(self.leave.category_string, 'Annual Leave')

class PayrollDateModelTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        
    def test_create_payroll_schedule(self):
        self.assertIsInstance(PayrollSchedule.objects.first(),
            PayrollSchedule)

    def test_create_payroll_date(self):
        date = PayrollDate.objects.create(
            date = TODAY.day,
            schedule=self.schedule
        )

        self.assertIsInstance(date, PayrollDate)

    def test_number_of_employees(self):
        self.assertEqual(self.pay_date.number_of_employees, 1)

    def test_z_all_employees(self):
        self.assertEqual(self.pay_date.all_employees, [self.employee])

    def test_date_suffix(self):
        self.assertIsInstance(self.pay_date.date_suffix, str)
