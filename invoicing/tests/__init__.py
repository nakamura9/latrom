from .models import *
from .views import *

'''
from .model_util import InvoicingModelCreator
from django.test import TestCase

class SomeTestCase(TestCase):
    fixtures = ['common.json', 'accounts.json','employees.json', 'invoicing.json']
    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()

    def test_something(self):
        pass
'''