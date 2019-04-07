from employees.models import *
import datetime


class EmployeeModelCreator():
    def __init__(self, klass):
        self.cls = klass

    def create_paygrade(self):

        self.cls.grade = PayGrade.objects.create(
            name='Model Test Paygrade',
            salary=300,
            monthly_leave_days=1.5,
            hourly_rate=2,
            overtime_rate=3,
            overtime_two_rate=4,
        )
        return self.cls.grade

    def create_employee(self):
        if not hasattr(self.cls, 'grade'):
            self.create_paygrade()
        self.cls.employee = Employee.objects.create(
            first_name = 'second',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            hire_date=datetime.date.today(),
            title='test role',
            pay_grade = self.cls.grade,
        )

        return self.cls.employee 