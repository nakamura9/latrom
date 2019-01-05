from django.test import TestCase, Client 
from inventory.tests.models import create_test_inventory_models
from employees.tests.models import create_test_employees_models
from services.models import *
import urllib
import json

class BasicServiceViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            **{'name': 'name', 'description': 'description'}   
        )
        return super().setUpTestData()

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_dashboard_page(self):
        resp = self.client.get('/services/')
        self.assertEqual(resp.status_code, 200)

    def test_get_create_category_page(self):
        resp = self.client.get('/services/create-category')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_category_page(self):
        resp = self.client.post('/services/create-category',
            data={'name': 'name', 'description': 'description'})
        self.assertEqual(resp.status_code, 302)

    def test_get_category_update_page(self):
        resp = self.client.get('/services/update-category/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_category_update_page(self):
        resp = self.client.post('/services/update-category/1',
            data={'name': 'name', 'description': 'other description'})
        self.assertEqual(resp.status_code, 302)

    def test_get_category_detail_page(self):
        resp = self.client.get('/services/category-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_category_list_page(self):
        resp = self.client.get('/services/category-list')
        self.assertEqual(resp.status_code, 200)


class ServicePersonnelViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            **{'name': 'name', 'description': 'description'}   
        )
        cls.service_person = ServicePerson.objects.create(
            employee=cls.employee
        )
        cls.service_team = ServiceTeam.objects.create(
            name="name",
            description="description"
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_service_person_creation_page(self):
        resp = self.client.get('/services/service-person-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_person_creation_page(self):
        resp = self.client.post('/services/service-person-create', 
            data={
                'employee': 1,
                'is_manager': True,
                'can_authorize_equipment_requisitions': True,
                'can_authorize_consumables_requisitions': True,
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_service_person_update_page(self):
        resp = self.client.get('/services/service-person-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_person_update_page(self):
        resp = self.client.post('/services/service-person-update/1', 
            data={
                'is_manager': False,
                'can_authorize_equipment_requisitions': True,
                'can_authorize_consumables_requisitions': True,
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_service_person_detail_page(self):
        resp = self.client.get('/services/service-person-dashboard/1')
        self.assertEqual(resp.status_code, 200)

    def test_service_person_list_page(self):
        resp = self.client.get('/services/service-person-list/')
        self.assertEqual(resp.status_code, 200)

    def test_get_team_create_page(self):
        resp = self.client.get('/services/team-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_team_create(self):
        resp = self.client.post('/services/team-create', data={
            'name': 'name',
            'description': 'descritopm',
            'manager': 1,
            'members': urllib.parse.quote(json.dumps([{
                'value': '1 - Service'
            }]))
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_team_update_page(self):
        resp = self.client.get('/services/team-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_team_update(self):
        resp = self.client.post('/services/team-update/1', data={
            'name': 'name',
            'description': 'descritopm',
            'manager': 1,
            'members': urllib.parse.quote(json.dumps([{
                'value': '1 - Service'
            }]))
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_service_team_detail_page(self):
        resp = self.client.get('/services/team-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_service_team_list_page(self):
        resp = self.client.get('/services/team-list')
        self.assertEqual(resp.status_code, 200)

        

class ServiceProcedureViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_inventory_models(cls)
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name='Name',
            reference="ref",
            description="desc",
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_service_procedure_page(self):
        resp = self.client.get('/services/create-procedure')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_procedure(self):
        resp = self.client.post('/services/create-procedure', 
            data={
                'tasks': urllib.parse.quote(json.dumps([
                    'some task'
                ])),
                'equipment': urllib.parse.quote(json.dumps([
                    {'value': '1 - item'}
                ])),
                'consumables': urllib.parse.quote(json.dumps([
                    {'value': '1 - item'}
                ])),
                'as_checklist': True,
                'name': 'name',
                'description': 'some description',
                'reference': 'ref'
            })
        
        self.assertEqual(resp.status_code, 302)

    def test_get_list_procedure_page(self):
        resp = self.client.get('/services/list-procedures')
        self.assertEqual(resp.status_code, 200)

    def test_get_service_procedure_update_page(self):
        resp = self.client.get('/services/procedure-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_procedure_update(self):
        resp = self.client.post('/services/procedure-update/1', 
            data={
                'tasks': urllib.parse.quote(json.dumps([
                    'some task'
                ])),
                'equipment': urllib.parse.quote(json.dumps([
                    {'value': '1 - item'}
                ])),
                'consumables': urllib.parse.quote(json.dumps([
                    {'value': '1 - item'}
                ])),
                'as_checklist': True,
                'name': 'name',
                'description': 'some description',
                'reference': 'ref'
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_procedure_detail_page(self):
        resp = self.client.get('/services/procedure-detail/1')
        self.assertEqual(resp.status_code, 200)

    