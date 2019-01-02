from services.models import *
from django.test import TestCase
import datetime

from employees.tests.models import create_test_employees_models
from employees.models import Employee
from inventory.models import Equipment, Consumable, UnitOfMeasure
from inventory.tests.models import create_test_inventory_models

TODAY = datetime.date.today()

class ServiceModelTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        
        create_test_employees_models(cls)
        create_test_inventory_models(cls)

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

    def test_create_service_category(self):
        obj = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        self.assertIsInstance(obj, ServiceCategory)

    def test_create_service_person(self):
        employee = Employee.objects.create(
            first_name = 'First',
            last_name = 'Last',
            address = 'Model test address',
            email = 'test@mail.com',
            phone = '1234535234',
            hire_date=TODAY,
            title='test role',
            pay_grade = self.grade
        )

        obj = ServicePerson.objects.create(
            employee=employee,
            is_manager = True,
            can_authorize_equipment_requisitions = False,
            can_authorize_consumables_requisitions = True
        )

        self.assertIsInstance(obj, ServicePerson)

    def test_create_service_team(self):
        obj = ServiceTeam.objects.create(
            name="name",
            description="description",
            manager=self.service_person
        )

        self.assertIsInstance(obj, ServiceTeam)

    def test_create_service_work_order(self):
        obj = ServiceWorkOrder.objects.create(
            date=str(TODAY),
            time="17:00",
            description="desc",
            completed=False,
            expected_duration="00:30",
            actual_duration="00:45",
            comments=""
        )
        self.assertIsInstance(obj, ServiceWorkOrder)

    def test_create_equipment_requisition(self):
        obj = EquipmentRequisition.objects.create(
            date=TODAY,
            department="dept",
            reference="ref",
            requested_by=self.employee
        )
        self.assertIsInstance(obj, EquipmentRequisition)

        obj_2 = EquipmentRequisitionLine.objects.create(
            equipment=Equipment.objects.first(),
            quantity=1,
            quantity_returned=10,
            requesting_condition='good',
            returned_condition="good",
            requisition=obj
        )
        self.assertIsInstance(obj_2, EquipmentRequisitionLine)

    def test_create_consumables_requistion(self):
        obj = ConsumablesRequisition.objects.create(
            date=TODAY,
            department="dept",
            reference="ref",
            requested_by=self.employee
        )

        self.assertIsInstance(obj, ConsumablesRequisition)

        obj_2 = ConsumablesRequisitionLine.objects.create(
            consumable=Consumable.objects.first(),
            unit=UnitOfMeasure.objects.first(),
            quantity=0,
            returned=0,
            requisition=obj
        )

        self.assertIsInstance(obj_2, ConsumablesRequisitionLine)

    def test_create_service_procedure(self):
        obj = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )

        self.assertIsInstance(obj, ServiceProcedure)

        obj_2 = Task.objects.create(
            procedure=obj,
            description="Something"
        )

        self.assertIsInstance(obj_2, Task)
