from decimal import Decimal as D
from django.test import TestCase
from django.contrib.auth.models import User
from accounting.views.reports.balance_sheet import BalanceSheet
from accounting.views.reports.trial_balance import TrialBalance
from inventory.tests import create_test_inventory_models
from invoicing.tests.models import create_test_invoicing_models
from employees.tests import create_test_employees_models
from employees.models import EmployeesSettings
from invoicing.models import (SalesInvoice, 
                            SalesInvoiceLine,
                            ServiceInvoice,
                            ServiceInvoiceLine,
                            Bill,
                            BillLine,
                            CombinedInvoice,
                            CombinedInvoiceLine,
                            SalesRepresentative, 
                            Payment,
                            CreditNote)
from inventory.models import (WareHouse,
                                UnitOfMeasure,
                                Supplier,
                                Category,
                                Product,
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

import datetime

TODAY = datetime.date.today()

class ReportTests(TestCase):
    fixtures = ['accounts.json', 'journals.json', 'settings.json', 'common.json', 'employees.json', 'inventory.json', 'invoicing.json', 'planner.json']
    
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        create_test_employees_models(cls)
        #common
        cls.warehouse = WareHouse.objects.create(
            name='Test Location',
            address='Test Address'
        )

        cls.supplier = Supplier.objects.create(
            organization=cls.organization,
            )

        cls.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        cls.unit = UnitOfMeasure.objects.create(
            name='Test Unit',
            description='Test description'
        )
        
        cls.product = Product.objects.create(
            name='test name',
            unit=cls.unit,
            pricing_method=0, #KISS direct pricing
            direct_price=10,
            margin=0.5,
            unit_purchase_price=10,
            description='Test Description',
            supplier = cls.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = cls.category
        )

        
        cls.exp = Expense.objects.create(
            date=TODAY,
            billable=True,
            customer=cls.customer_org,
            amount=10,
            description="test description",
            category=0,
            debit_account=Account.objects.first()
        )
        #sales invoice 
        
        cls.sales_inv = SalesInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
            ship_from=cls.warehouse,
            )
        cls.line = SalesInvoiceLine.objects.create(
            product=cls.product,
            quantity=1,
            invoice=cls.sales_inv,
        )

        #service invoice
        cls.service_inv = ServiceInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
        )
        cat = ServiceCategory.objects.create(
            name="name"
        )
        cls.service = Service.objects.create(
            name="Test Service",
            description="some description",
            flat_fee=10,
            hourly_rate=1,
            frequency="once",
            category=cat
        )

        cls.service_line = ServiceInvoiceLine.objects.create(
            invoice=cls.service_inv,
            service=cls.service,
            hours=0
        )

        #bill
        cls.bill_inv = Bill.objects.create(
            customer_reference="100",
            status='invoice',
            customer=cls.customer_org,
        )
        cls.bil_line = BillLine.objects.create(
            bill=cls.bill_inv,
            expense=cls.exp
            )

        #combined
        cls.combined_inv = CombinedInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
        )

        cls.line_sale = CombinedInvoiceLine.objects.create(
            invoice=cls.combined_inv,
            product=cls.product,
            line_type=1,
            quantity_or_hours=1
        )
        cls.line_service = CombinedInvoiceLine.objects.create(
            invoice=cls.combined_inv,
            service=cls.service,
            line_type=2,
            quantity_or_hours=0
        )
        cls.line_bill = CombinedInvoiceLine.objects.create(
            invoice=cls.combined_inv,
            expense=cls.exp,
            line_type=3,
            quantity_or_hours=0
        )

        cls.order = Order.objects.create(
            expected_receipt_date = TODAY,
            date = TODAY,
            tax = Tax.objects.first(), #10%
            supplier=cls.supplier,
            bill_to = 'Test Bill to',
            ship_to = cls.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'draft'
        )
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=1,
            order_price=10,
        )

        cls.asset = Asset.objects.create(
            name='Test Asset',
            description='Test description',
            category = 0,
            initial_value = 100,
            credit_account = Account.objects.get(pk=1000),
            depreciation_period = 5,
            init_date = TODAY,
            depreciation_method = 0,
            salvage_value = 20,
        )

        cls.payment = Payment.objects.create(
            payment_for=0,
            sales_invoice=cls.sales_inv,
            amount=10,
            date=TODAY,
            sales_rep=SalesRepresentative.objects.first()
        )

        cls.employee.user = User.objects.create_user(username="tstusr")
        cls.employee.save()
        es = EmployeesSettings.objects.first()
        es.payroll_officer = cls.employee
        es.save()

        cls.credit_note = CreditNote.objects.create(
            date=TODAY,
            invoice=cls.sales_inv,
            comments="Test comment"
        )

        cls.debit_note = DebitNote.objects.create(
            date=datetime.date.today(),
            order=cls.order,
            comments= "comment"
        )

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

    def test_sales_invoice(self):
        print("Testing Sales Invoice")
        self.sales_inv.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    
    def test_service_invoice(self):
        print("Testing Service Invoice")
        self.service_inv.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())
    
    def test_bill(self):
        print("Testing Bill")
        self.bill_inv.create_entry()
        self.assertTrue(self.trialBalanceInBalance())
        self.assertTrue(self.balanceSheetInBalance())

    def test_combined_invoice(self):
        print("Testing Combined Invoice")
        self.combined_inv.create_entry()
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
        self.exp.create_entry()
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