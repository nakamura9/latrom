import datetime
import json
import urllib

from django.test import TestCase, Client
from django.contrib.auth.models import User
from planner.models import *
from employees.tests.models import create_test_employees_models
from common_data.tests import create_test_common_entities

from common_data.models import Organization
from inventory.models import Supplier
from invoicing.models import Customer

TODAY = datetime.date.today()

class PlannerAPIViewTests(TestCase):
    fixtures = ['common.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        
    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_superuser('User', 'abc@xyz.com', '123')
        create_test_common_entities(cls)
        cls.evt = Event.objects.create(
            date=TODAY,
            reminder=datetime.timedelta(hours=1),
            start_time=datetime.datetime.now().time(),
            end_time=datetime.datetime.now().time(),
            owner=cls.usr
        )
        
        cls.month = TODAY.month
        cls.day = TODAY.day
        cls.year, cls.week, cls.weekday = TODAY.isocalendar()

    def setUp(self):
        self.client.login(username='User', password='123')

    def test_get_month_api_view(self):
        resp = self.client.get('/planner/api/calendar/month/{}/{}'.format(
            self.year, self.month
        ))
        self.assertEqual(resp.status_code, 200)
    
    def test_get_week_api_view(self):
        resp = self.client.get('/planner/api/calendar/day/{}/{}/{}'.format(
            self.year, self.month, self.day
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(json.loads(resp.content)['events']['events']), 1)
        

    def test_get_day_api_view(self):
        resp = self.client.get('/planner/api/calendar/month/{}/{}'.format(
            self.year, self.month, self.day
        ))
        self.assertEqual(resp.status_code, 200)


class PlannerViewTests(TestCase):
    fixtures = ['planner.json', 'accounts.json', 'common.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_superuser('User', 'abc@xyz.com', '123')
        create_test_employees_models(cls)

        cls.evt = Event.objects.create(
            date=TODAY,
            reminder=datetime.timedelta(hours=1),
            start_time=datetime.datetime.now().time(),
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
        cls.employee.user = cls.usr 
        cls.employee.save()
        create_test_common_entities(cls)


    def setUp(self):
        self.client.login(username='User', password='123')
    
    def test_get_calendar_page(self):
        resp = self.client.get('/planner/calendar')
        self.assertEqual(resp.status_code, 200)

    def test_get_dashboard(self):
        resp = self.client.get('/planner/dashboard')
        self.assertEqual(resp.status_code, 200)

    def test_get_planner_config_page(self):
        resp = self.client.get('/planner/config/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_create_event_page(self):
        resp = self.client.get('/planner/event-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_event_create_page(self):
        resp = self.client.post('/planner/event-create', 
            data={
                'owner': 1,
                'date': TODAY,
                'label': 'caleb',
                'reminder': '0:15:00',
                'start_time': '06:00:00', 
                'end_time': '06:00:00',
                'priority': 'normal',
                'description': 'Desc',
                'repeat': 0,
                'json_participants': urllib.parse.quote(json.dumps([{
                    'type': 'employee',
                    'pk': '1'
                }]))
            })
        
        self.assertEqual(resp.status_code, 302)

    def test_get_event_update_page(self):
        resp = self.client.get('/planner/event-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_event_update_page(self):
        resp = self.client.post('/planner/event-update/1', 
            data={
                'owner': 1,
                'date': TODAY,
                'label': 'caleb',
                'reminder': '0:15:00',
                'start_time': '06:00:00', 
                'end_time': '06:00:00',
                'priority': 'normal',
                'description': 'Desc',
                'json_participants': urllib.parse.quote(json.dumps([{
                    'type': 'employee',
                    'pk': '1'
                }])),
                'repeat': 0
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_event_list(self):
        resp = self.client.get('/planner/event/list')
        self.assertEqual(resp.status_code, 200)

    def test_get_event_list(self):
        resp = self.client.get('/planner/event-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_event_list(self):
        resp = self.client.get('/planner/agenda/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_event_complete_view(self):
        resp = self.client.get('/planner/event-complete/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_event_delete_view(self):
        resp = self.client.get('/planner/event-delete/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_event_delete_view(self):
        resp = self.client.post('/planner/event-delete/1')
        self.assertEqual(resp.status_code, 302)

    def test_get_event_complete_view(self):
        resp = self.client.post('/planner/event-complete/1')
        self.assertEqual(resp.status_code, 302)