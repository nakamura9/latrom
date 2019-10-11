from decimal import Decimal as D
from django.test import TestCase
from django.contrib.auth.models import User
from accounting.views.reports.balance_sheet import BalanceSheet
from accounting.views.reports.trial_balance import TrialBalance
from employees.tests import create_test_employees_models
from employees.models import EmployeesSettings
from invoicing.models import (Invoice,
                            InvoiceLine,
                            SalesRepresentative, 
                            Payment,
                            ProductLineComponent,
                            ServiceLineComponent,
                            ExpenseLineComponent,
                            CreditNote)
from inventory.models import (WareHouse,
                                UnitOfMeasure,
                                Supplier,
                                Category,
                                InventoryItem,
                                ProductComponent,
                                Order,
                                OrderItem,
                                DebitNote)
from services.models import (Service,
                            ServiceCategory,
                            )
from accounting.models import (Account,
                                Expense,
                                Tax,
                                Asset,
                                Journal,
                                JournalEntry)

from common_data.tests.model_util import CommonModelCreator
from invoicing.tests.model_util import InvoicingModelCreator
from inventory.tests.model_util import InventoryModelCreator

import datetime

TODAY = datetime.date.today()

class ReportTests(TestCase):
    fixtures = ['accounts.json', 'journals.json', 'settings.json', 'common.json', 'employees.json', 'inventory.json', 'invoicing.json', 'planner.json', 'payroll.json']
    
    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        #common
        cls.usr = User.objects.create_user(username="tstusr")

        InventoryModelCreator(cls).create_all()
        InvoicingModelCreator(cls).create_all()
        cls.product.unit_purchase_price = 0
        cls.product.save()

        cls.asset = Asset.objects.create(
            name='Test Asset',
            created_by=cls.usr,
            description='Test description',
            category = 0,
            initial_value = 100,
            credit_account = Account.objects.get(pk=1000),#cash
            depreciation_period = 5,
            init_date = TODAY,
            depreciation_method = 0,
            salvage_value = 20,
        )

        cls.employee.user = cls.usr 
        cls.employee.save()
        es = EmployeesSettings.objects.first()
        es.payroll_officer = cls.officer
        es.save()


    def tearDown(self):
        self.customer_org.account.balance = D(0)
        self.customer_org.account.save()


    def balanceSheetInBalance(self):
        '''Assets - liabilities = equity'''

        context = BalanceSheet.common_context({})
        print(f"Balance Sheet: {context['net_assets']} {context['equity_total']}")
        return context['net_assets'] == context['equity_total']  
    
    def trialBalanceInBalance(self):
        context = TrialBalance.common_context({})
        print(f"Trial balance: {context['total_debit']}"
            f" {context['total_credit']}")
        return context['total_debit'] == context['total_credit']

    def test_initial_status(self):
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    
    def test_sales_invoice(self):
        print("Testing Invoice")
        print('invoice total ', self.invoice.total)
        self.invoice.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    
    
    def test_purchase_order(self):
        print("Testing Purchase Order")
        self.order.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    
    def test_create_asset(self):
        print("Testing Assets")
        self.asset.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    
    def test_record_expense(self):
        print("Testing Recording expense")
        self.expense.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    def test_create_payslip(self):

        print("Testing Payslip")
        self.slip.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    def test_create_invoice_payment(self):
        print("Testing Payslip")
        
        self.payment.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    def test_credit_note(self):
        print("Testing Credit Note")
        
        self.credit_note.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    
    def test_debit_note(self):
        print("Testing Debit Note")
        
        self.debit_note.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())


    def test_carriage_outwards(self):
        # simple expense without a seperate model
        print('Testing carriage outwards')
        expense = Expense.objects.create(
            category=11,
            amount=100,
            description='description',
            debit_account=Account.objects.get(pk=1000),
            recorded_by=self.employee.user,
            date=TODAY
        )

        expense.create_entry()

        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())



    def test_carriage_inwards(self):
        #simple form view without corresponding model, replicate with a 
        #function call
        print('Testing carriage inwards')

        entry = JournalEntry.objects.create(
            date=TODAY, 
            memo='memo', 
            journal=Journal.objects.get(pk=2),#disbursements
            created_by=self.employee.user,
            draft=False
        )
        # the unit cost changes but the journal entry for the cost 
        # of the order remains the same
        entry.simple_entry(
            100,
            Account.objects.get(pk=1000),
            Account.objects.get(pk=4009)
            )

        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    