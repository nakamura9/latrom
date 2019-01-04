from django.test import TestCase, Client 
from inventory.tests.models import create_test_inventory_models
from employees.tests.models import create_test_employees_models
from services.models import *

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
        return super().setUpTestData()

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_service_person_creation_page(self):
        pass

    def test_post_service_person_creation_page(self):
        pass