from services.models import *
from django.test import TestCase
import datetime
from decimal import Decimal as D

from employees.tests.models import create_test_employees_models
from employees.models import Employee
from inventory.models import InventoryItem, UnitOfMeasure
import inventory
from accounting.models import Expense, Account
from invoicing.models import (Invoice, 
                                InvoiceLine, 
                                Customer, 
                                ServiceLineComponent)
from services.models import Service, ServiceCategory, TimeLog
from employees.models import Employee

TODAY = datetime.date.today()

class ServiceModelTests(TestCase):
    fixtures = ['common.json','inventory.json', 
        'accounts.json', 'employees.json', 'invoicing.json']

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        inventory.tests.models.create_test_inventory_models(cls)

        cls.category = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )
        cls.service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=cls.category,
            procedure=cls.procedure,
            frequency='once',
            is_listed=True
        )

        cls.inv = Invoice.objects.create(
            status='invoice',
            customer=Customer.objects.first(),
        )
        cls.cat = ServiceCategory.objects.create(
            name="name"
        )

        slc = ServiceLineComponent.objects.create(
            service=cls.service,
            hours=0,
            flat_fee=100,
            hourly_rate=10
        )

        cls.line = InvoiceLine.objects.create(
            invoice=cls.inv,
            service = slc,
            line_type = 2
        )

        cls.service_person = ServicePerson.objects.create(
            employee=cls.employee,
            is_manager = True,
            can_authorize_equipment_requisitions = False,
            can_authorize_consumables_requisitions = True
        )


    def test_create_service(self):
        obj = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=self.category,
            procedure=self.procedure,
            frequency='once',
            is_listed=True
        )
        self.assertIsInstance(obj, Service)
        self.assertIsInstance(str(obj), str)

    def test_create_service_category(self):
        obj = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        self.assertIsInstance(obj, ServiceCategory)
        self.assertEqual(obj.service_count, 0)


    def test_create_service_person(self):
        employee = Employee.objects.create(
            first_name = 'First',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            pay_grade = self.grade
        )

        obj = ServicePerson.objects.create(
            employee=employee,
            is_manager = True,
            can_authorize_equipment_requisitions = False,
            can_authorize_consumables_requisitions = True
        )

        self.assertIsInstance(obj, ServicePerson)
        self.assertIsInstance(str(obj), str)


    def test_create_service_team(self):
        obj = ServiceTeam.objects.create(
            name="name",
            description="description",
            manager=self.service_person
        )

        self.assertIsInstance(obj, ServiceTeam)
        self.assertIsInstance(str(obj), str)

    

    def test_create_equipment_requisition(self):
        obj = EquipmentRequisition.objects.create(
            date=TODAY,
            reference="ref",
            requested_by=self.employee
        )
        self.assertIsInstance(obj, EquipmentRequisition)
        self.assertIsInstance(str(obj), str)
        

        obj_2 = EquipmentRequisitionLine.objects.create(
            equipment=InventoryItem.objects.filter(type=1).first(),
            quantity=1,
            quantity_returned=10,
            requesting_condition='good',
            returned_condition="good",
            requisition=obj
        )
        self.assertIsInstance(obj_2, EquipmentRequisitionLine)
        self.assertIsInstance(str(obj_2), str)

    def test_create_consumables_requistion(self):
        obj = ConsumablesRequisition.objects.create(
            date=TODAY,
            reference="ref",
            requested_by=self.employee
        )

        self.assertIsInstance(obj, ConsumablesRequisition)

        obj_2 = ConsumablesRequisitionLine.objects.create(
            consumable=InventoryItem.objects.filter(type=2).first(),
            unit=UnitOfMeasure.objects.first(),
            quantity=0,
            returned=0,
            requisition=obj
        )

        self.assertIsInstance(obj_2, ConsumablesRequisitionLine)
        self.assertIsInstance(str(obj_2), str)


    def test_create_service_procedure(self):
        obj = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )

        self.assertIsInstance(obj, ServiceProcedure)
        self.assertIsInstance(str(obj), str)


        obj_2 = Task.objects.create(
            procedure=obj,
            description="Something"
        )

        self.assertIsInstance(obj_2, Task)
        self.assertIsInstance(str(obj_2), str)
        
        self.assertEqual(obj.steps.count(), 1)


class WorkOrderModelTests(TestCase):
    fixtures = ['common.json','inventory.json', 
        'accounts.json', 'employees.json', 'invoicing.json']

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        inventory.tests.models.create_test_inventory_models(cls)


        cls.category = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )

        cls.step = Task.objects.create(
            procedure=cls.procedure,
            description="some text"
        )
        cls.service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=cls.category,
            procedure=cls.procedure,
            frequency='once',
            is_listed=True
        )

        cls.inv = Invoice.objects.create(
            status='invoice',
            customer=Customer.objects.first(),
        )
        cls.cat = ServiceCategory.objects.create(
            name="name"
        )
        
        slc = ServiceLineComponent.objects.create(
            service=cls.service,
            hours=0,
            flat_fee=100,
            hourly_rate=10
        )

        cls.line = InvoiceLine.objects.create(
            invoice=cls.inv,
            service = slc,
            line_type = 2
        )

        cls.service_person = ServicePerson.objects.create(
            employee=cls.employee,
            is_manager = True,
            can_authorize_equipment_requisitions = False,
            can_authorize_consumables_requisitions = True
        )

        cls.wr = WorkOrderRequest.objects.create(
            status="request",
            service=cls.service,
            invoice=cls.inv
        )
        cls.wo = ServiceWorkOrder.objects.create(
            date=str(TODAY),
            time="17:00",
            description="desc",
            completed=datetime.datetime.now(),
            expected_duration=datetime.timedelta(seconds=3600),
            works_request = cls.wr
        )
        cls.wo.service_people.add(cls.service_person)
        cls.wo.save()

        cls.log = TimeLog.objects.create(
            work_order=cls.wo,
            employee=cls.employee,
            date=datetime.date.today(),
            normal_time=datetime.timedelta(seconds=3600),
            overtime=datetime.timedelta(seconds=3600),
        )

        cls.exp = Expense.objects.create(
            description="things",
            category=0,
            amount=10,
            debit_account=Account.objects.get(pk=1000),
            date=datetime.date.today()
        )

        cls.wo_exp = WorkOrderExpense.objects.create(
            work_order=cls.wo,
            expense=cls.exp
        )

    def test_create_service_work_order(self):
        
        obj = ServiceWorkOrder.objects.create(
            date=str(TODAY),
            time="17:00",
            description="desc",
            completed=datetime.datetime.now(),
            expected_duration=datetime.timedelta(seconds=3600),
            works_request = self.wr
        )
        self.assertIsInstance(obj, ServiceWorkOrder)
        self.assertIsInstance(str(obj), str)

    def test_create_work_order_expense(self):
        obj = WorkOrderExpense.objects.create(
            work_order=self.wo,
            expense=self.exp
        )

        self.assertIsInstance(obj, WorkOrderExpense)

        obj.delete()

    def test_create_works_request(self):
        service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=self.category,
            procedure=self.procedure,
            frequency='once',
            is_listed=True
        )
        obj = WorkOrderRequest.objects.create(
            status="request",
            service=service,
            invoice=self.inv
        )
        self.assertIsInstance(obj, WorkOrderRequest)

    def test_create_time_log(self):
        obj = TimeLog.objects.create(
            work_order=self.wo,
            employee=Employee.objects.first(),
            date=datetime.date.today(),
            normal_time=datetime.timedelta(seconds=3600),
            overtime=datetime.timedelta(seconds=3600),
        )
        self.assertIsInstance(obj, TimeLog)
        obj.delete()

    def test_work_order_request_update_status(self):
        self.assertEqual(self.wr.status, "in-progress")
        self.wo.status= "completed"
        self.wo.save()
        self.wr.update_status()
        self.assertEqual(self.wr.status, "completed")


    def test_work_order_request_invoice(self):
        self.assertIsInstance(self.wr.invoice, Invoice)

    def test_work_order_request_work_orders(self):
        self.assertEqual(self.wr.work_orders.count(), 1)

    def test_time_log_total_cost(self):
        self.assertEqual(self.log.total_cost, D(5))

    def test_work_order_procedure_pk(self):
        self.assertIsInstance(self.wo.procedure_pk, int)

    def test_number_employees_work_order(self):
        self.assertEqual(self.wo.number_of_employees, 1)

    def test_expenses_work_order(self):
        self.assertEqual(self.wo.expenses.count(), 1)

    def test_time_logs_work_orders(self):
        self.employee.uses_timesheet = True
        self.employee.save()

        self.assertEqual(self.wo.time_logs.count(), 1)

        self.employee.uses_timesheet = False
        self.employee.save()
        
    def test_work_order_progress_list(self):
        self.assertEqual(self.wo.progress_list, [])

    def test_work_order_progress_percentage(self):
        self.assertEqual(self.wo.progress_percentage, 0)
        

    def test_work_order_normal_hours(self):
        self.assertEqual(self.wo.total_normal_time, datetime.timedelta(seconds=3600))

    def test_work_order_total_overtime(self):
        self.assertEqual(self.wo.total_overtime, datetime.timedelta(seconds=3600))
        