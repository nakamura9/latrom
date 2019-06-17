from django.test import TestCase, Client
from accounting.models import Account
from common_data.tests import create_test_user

class ReportTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'journals.json', 'settings.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_something(self):
        resp = self.client.get('/accounting/csv/balance-sheet/')
        self.assertTrue(resp.status_code == 200)


















    #setupclass
    #setuptestdata
    #for test in tests
        #setup
        #test
        #tearDown