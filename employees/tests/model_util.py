from employees.models import *
import datetime
from django.contrib.auth.models import User

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

        if not hasattr(self.cls, 'employee_user'):    
            self.create_employee_user()

        self.cls.employee = Employee.objects.create(
            first_name = 'second',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            pay_grade = self.cls.grade,
            user=self.cls.employee_user
        )

        return self.cls.employee 

    def create_employee_user(self):
        self.cls.employee_user = User.objects.create(
            username="employee_user"
        )