from django.test import Client, TestCase, RequestFactory
from employees.services import AutomatedPayrollService
from employees.views import  ManualPayrollService
from employees.models import *
from .models import create_test_employees_models
import datetime
from django.contrib.auth.models import User



TODAY = datetime.date.today() 

class AutomatedServiceTests(TestCase):
    fixtures = ['accounts.json', 'employees.json', 'common.json']
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.settings = EmployeesSettings.objects.first()
        cls.settings.payroll_officer=cls.officer
        cls.service = AutomatedPayrollService()

    def test_create_service(self):
        obj = AutomatedPayrollService()
        self.assertIsInstance(obj, AutomatedPayrollService)

    def test_run_payroll_service(self):
        obj = AutomatedPayrollService()
        obj.run()
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

        self.assertEqual(Employee.objects.get(pk=self.employee.pk).leave_days,
            prev_days + self.employee.pay_grade.monthly_leave_days)

        Leave.objects.create(
            start_date=datetime.date(2018,1,1),
            end_date=datetime.date(2018,1,3),
            employee=self.employee,
            category=1,
            status=1,
        )

        prev_days = Employee.objects.get(pk=self.employee.pk).leave_days

        self.service.adjust_leave_days()
        self.assertTrue(prev_days != Employee.objects.get(pk=self.employee.pk).leave_days)
    

class ManualServiceTests(TestCase):
    fixtures = ['accounts.json', 'employees.json']
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        cls.settings = EmployeesSettings.objects.first()
        cls.settings.payroll_officer =cls.officer
        cls.settings.save()
        
        cls.usr = User.objects.create_superuser(
            'Testuser', 'admin@test.com', '123')
        cls.employee.user = cls.usr
        cls.employee.save()
        
        cls.form_data = {
            'employees': Employee.objects.all(),
            'start_period': TODAY,
            'end_period': TODAY,
            'payroll_officer': cls.employee
        }
        cls.request =  RequestFactory()
        
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(cls.request, 'session', 'session')
        messages = FallbackStorage(cls.request)
        setattr(cls.request, '_messages', messages)
        
        cls.service = ManualPayrollService(cls.form_data,cls.request)
    
    def setUp(self):
        self.employee_two = Employee.objects.create(
            first_name = 'Second',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            pay_grade = self.grade
        )
    
    def tearDown(self):
        self.employee_two.hard_delete()

    def test_create_service(self):
        obj = ManualPayrollService(self.form_data, self.request)
        self.assertIsInstance(obj, ManualPayrollService)

    def test_manual_payroll_service_run(self):
        Payslip.objects.all().delete()
        self.service.run()
        self.assertEqual(Payslip.objects.all().count(), 
            Employee.objects.all().count())

    def test_existing_payslip(self):
        self.assertTrue(self.service.check_existing_payslip(self.employee))
        self.assertFalse(self.service.check_existing_payslip(self.employee_two))

    def test_generate_salaried_payslip(self):
        self.employee_two.uses_timesheet=False
        self.employee_two.save()
        obj = self.service.generate_salaried_payslip(self.employee_two)
        self.assertIsInstance(obj, Payslip)

    def test_get_timesheet_generate_wages_payslip(self):
        sheet = EmployeeTimeSheet.objects.create(
            employee=self.employee_two,
            month=TODAY.month,
            year=TODAY.year,
            recorded_by=self.employee_two,
            complete=True
        )

        line = AttendanceLine.objects.create(
            timesheet=sheet,
            date= TODAY, 
            time_in = datetime.datetime(2018, 1, 1, 8, 0).time(),
            time_out = datetime.datetime(2018, 1, 1, 17, 0).time(),
        )

        sheet_obj = self.service.get_employee_timesheet(self.employee_two)
        self.assertIsInstance(sheet_obj, EmployeeTimeSheet)

        obj = self.service.generate_wage_payslip(self.employee_two)
        self.assertIsInstance(obj, Payslip)

    def test_adjust_leave_days(self):
        Leave.objects.create(
            start_date=TODAY,
            end_date=TODAY,
            employee=self.employee_two,
            category=1,
            status=1,
        )

        pre_leave_days = self.employee_two.leave_days
        self.service.adjust_leave_days(self.employee_two)
        self.assertNotEqual(pre_leave_days, self.employee_two.leave_days)
