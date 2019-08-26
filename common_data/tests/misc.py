from django.test import Client, TestCase 
from django.test.client import RequestFactory
import datetime
from django.shortcuts import reverse
#from invoicing.tests.model_util import InvoicingModelCreator
from invoicing.views import CustomerStatementPDFView

class ReportViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        #InvoicingModelCreator(cls).create_all()
        pass 

    
