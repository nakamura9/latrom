import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from planner.models import *
from employees.tests.models import create_test_employees_models
from common_data.models import Organization
from inventory.models import Supplier
from invoicing.models import Customer

TODAY = datetime.date.today()
class PlannerModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="user")
        
        create_test_employees_models(cls)

        cls.evt = Event.objects.create(
            date=TODAY,
            reminder=datetime.timedelta(hours=1),
            start_time=datetime.datetime.now().time(),
            end_time=datetime.datetime.now().time(),
            owner=cls.usr
        )

        cls.organization = Organization.objects.create(
            legal_name = 'test business'
        )

        cls.supplier = Supplier.objects.create(
            organization=cls.organization
            )

        cls.customer = Customer.objects.create(
        organization= cls.organization
    )

    def setUp(self):
        pass

    def test_create_event(self):
        obj = Event.objects.create(
            date=TODAY,
            reminder=datetime.timedelta(hours=1),
            start_time=datetime.datetime.now().time(),
            end_time=datetime.datetime.now().time(),            
            owner=self.usr
        )

        self.assertIsInstance(obj, Event)
        self.assertIsInstance(str(obj), str)

    def test_complete_event(self):
        self.evt.complete()
        self.assertTrue(self.evt.completed)

    def test_create_employee_participant(self):
        prev_count = Event.objects.first().participants.count()
        self.evt.add_participant('employee', 1)
        
        self.assertEqual(Event.objects.first().participants.count(),
            prev_count + 1)

    def test_create_event_customer_participant(self):
        prev_count = Event.objects.first().participants.count()
        self.evt.add_participant('customer', 1)
        
        self.assertEqual(Event.objects.first().participants.count(),
            prev_count + 1)
    
    def test_create_event_supplier_participant(self):
        prev_count = Event.objects.first().participants.count()
        self.evt.add_participant('supplier', 1)
        
        self.assertEqual(Event.objects.first().participants.count(),
            prev_count + 1)

    def test_create_planner_config(self):
        obj = PlannerConfig.objects.create(
            number_of_agenda_items=10,
            autogenerate_events_from_models=True
        )

        self.assertIsInstance(obj, PlannerConfig)

    def test_create_event_participant(self):
        obj = EventParticipant.objects.create(
            participant_type=0,
            employee=self.employee
        )

        self.assertIsInstance(obj, EventParticipant)
        self.assertIsInstance(str(obj), str)