from django.test import Client, TestCase
from employees.views import AutomatedPayrollService, ManualPayrollService
from employees.models import *
from .models import create_test_employees_models
import datetime

TODAY = datetime.date.today() 

class AutomatedServiceTests(TestCase):
    fixtures = ['accounts.json']
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.settings = EmployeesSettings.objects.create(
            payroll_date_one=datetime.date.today().day,
            payroll_cycle="monthly",
            payroll_officer=cls.employee
        )
        cls.settings.automate_payroll_for.set(Employee.objects.all())
        cls.service = AutomatedPayrollService()

    def test_create_service(self):
        obj = AutomatedPayrollService()
        self.assertIsInstance(obj, AutomatedPayrollService)

    def test_run_payroll_service(self):
        obj = AutomatedPayrollService()
        obj.run()
        self.assertEqual(Payslip.objects.count(), 2)
        Payslip.objects.latest('pk').delete()

    def test_run_salaries_payroll(self):
        self.service.run_salaries_payroll(1)
        
        self.assertEqual(Payslip.objects.count(), 2)
        Payslip.objects.latest('pk').delete()

    def test_run_wages_payroll(self):
        wage_employee = Employee.objects.create(
            first_name = 'Second',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            hire_date=TODAY,
            title='test role',
            pay_grade = self.grade,
            uses_timesheet=True
        )

        sheet = EmployeeTimeSheet.objects.create(
            employee=wage_employee,
            month=TODAY.month,
            year=TODAY.year,
            recorded_by=self.employee,
            complete=True
        )

        line = AttendanceLine.objects.create(
            timesheet=sheet,
            date= TODAY, 
            time_in = datetime.datetime(2018, 1, 1, 8, 0).time(),
            time_out = datetime.datetime(2018, 1, 1, 17, 0).time(),
        )

        self.settings.automate_payroll_for.set(Employee.objects.all())

        self.service.run_wages_payroll(1)

        self.assertEqual(Payslip.objects.count(), 2)
        Payslip.objects.latest('pk').delete()

    def test_get_employees_timesheet(self):
        sheet = EmployeeTimeSheet.objects.create(
            employee=self.employee,
            month=TODAY.month,
            year=TODAY.year,
            recorded_by=self.employee,
            complete=True
        )
        res = self.service.get_employee_timesheet(self.employee)
        self.assertIsInstance(res, EmployeeTimeSheet)

    def test_adjust_employee_leave_days(self):
        prev_days = self.employee.leave_days
        self.employee.last_leave_day_increment = None
        self.employee.save()
        
        self.service.adjust_leave_days()


        self.assertEqual(Employee.objects.first().leave_days,
            prev_days + self.employee.pay_grade.monthly_leave_days)

        Leave.objects.create(
            start_date=datetime.date(2018,1,1),
            end_date=datetime.date(2018,1,3),
            employee=self.employee,
            category=1,
            status=1,
        )

        prev_days = Employee.objects.first().leave_days

        self.service.adjust_leave_days()
        self.assertTrue(prev_days != Employee.objects.first().leave_days)


class ManualServiceTests(TestCase):
    fixtures = ['accounts.json']
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.settings = EmployeesSettings.objects.create(
            payroll_date_one=datetime.date.today().day,
            payroll_cycle="monthly",
            payroll_officer=cls.employee
        )
        cls.settings.automate_payroll_for.set(Employee.objects.all())
        form_data = {
            'employees': Employee.objects.all(),
            'start_period': TODAY,
            'end_period': TODAY
        }
        cls.service = ManualPayrollService(form_data)

    def test_manual_payroll_service_run(self):
        #self.service.run()
        pass



