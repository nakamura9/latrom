import datetime
from decimal import Decimal as D

from django.db.models import Q
from django.test import Client, TestCase
from django.urls import reverse

from accounting.models import Account, Expense, Tax, JournalEntry
from common_data.models import Individual, Organization
from common_data.tests import create_test_common_entities
from employees.models import Employee, PayGrade
from employees.tests import create_test_employees_models
from inventory.models import WareHouseItem
from inventory.tests import create_test_inventory_models
from invoicing.models import *
from services.models import Service, ServiceCategory

TODAY = datetime.date.today()

def create_test_invoicing_models(cls):
    '''creates common models for testing invoices.
    
    1. customers:
        a. customer_org
        b. customer_ind
    '''
    create_test_common_entities(cls)
    org = Organization.objects.create(
        legal_name="business"
        )
    ind = Individual.objects.create(
        first_name="test",
        last_name="last_name"
        )
    cls.customer_ind = Customer.objects.create(
        individual= ind
    )
    cls.customer_org = Customer.objects.create(
        organization= org
    )


class CommonModelTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json','invoicing.json']
        
    def test_update_sales_config(self):
        obj = SalesConfig.objects.get(pk=1)
        obj.default_invoice_comments = "Test comment"
        self.assertIsInstance(obj, SalesConfig)


class CustomerModelTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json','invoicing.json']
        
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        create_test_inventory_models(cls)

    def tearDown(self):
        for inv in SalesInvoice.objects.all():
            inv.delete()

    def test_create_individual_customer(self):
        obj = Customer.objects.create(
            individual=self.individual
        )
        self.assertIsInstance(obj, Customer)

    def test_create_organization_customer(self):
        obj = Customer.objects.create(
            organization=self.organization
        )
        self.assertIsInstance(obj, Customer)

    def test_customer_email(self):
        self.assertIsInstance(self.customer_org.customer_email, str)
        self.assertIsInstance(self.customer_ind.customer_email, str)

    def test_customer_name(self):
        self.assertIsInstance(self.customer_ind.name, str)
        self.assertIsInstance(self.customer_org.name, str)

    def test_customer_type(self):
        self.assertTrue(self.customer_org.is_organization)
        self.assertFalse(self.customer_ind.is_organization)

    def test_customer_account(self):
        self.assertIsInstance(self.customer_org.account, Account)

    def test_invoices(self):
        inv = SalesInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
            )
        
        self.assertEqual(len([i for i in self.customer_org.invoices]), 1)

    def test_credit_invoices(self):
        inv = SalesInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
            )
        
        self.assertEqual(len(self.customer_org.credit_invoices), 1)
        #once paid the credit should go down to zero
        inv.status='paid'
        inv.save()
        self.assertEqual(len(self.customer_org.credit_invoices), 0)

    def test_age_list(self):
        due = TODAY - datetime.timedelta(days=8)
        inv = SalesInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
            due= due
            )
        self.assertEqual(self.customer_org.age_list, [0, 1, 0, 0, 0, 0])

class PaymentModelTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json','invoicing.json']
        
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        create_test_inventory_models(cls)
        
        cls.sales_inv = SalesInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
            )
        SalesInvoiceLine.objects.create(
            product=cls.product,
            quantity=1,
            invoice=cls.sales_inv
        )

        cls.payment = Payment.objects.create(
            payment_for=0,
            sales_invoice=cls.sales_inv,
            amount=10,
            date=TODAY,
            sales_rep=SalesRepresentative.objects.first()
        )

    def test_create_payment(self):
        inv = SalesInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
            )
        SalesInvoiceLine.objects.create(
            product=self.product,
            quantity=1,
            invoice=inv
        )
        obj = Payment.objects.create(
            payment_for=0,
            sales_invoice=inv,
            amount=10,
            date=TODAY,
            sales_rep=SalesRepresentative.objects.first()
        )
        self.assertIsInstance(obj, Payment)

    def test_payment_invoice(self):
        self.assertIsInstance(self.payment.invoice, SalesInvoice)

    def test_payment_due(self):
        #invoice value = 10, no tax
        self.assertEqual(self.payment.due, 0)

    def test_create_entry(self):
        self.payment.create_entry()
        self.assertEqual(self.payment.invoice.customer.account.balance, D(10))


class SalesRepModelTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json','invoicing.json']
        
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        create_test_inventory_models(cls)
        cls.employee_two =  Employee.objects.create(
            hire_date=TODAY,
            pay_grade=PayGrade.objects.first(),
            first_name="T",
            last_name="U"
        )  

    def tearDown(self):
        SalesRepresentative.objects.get(employee=self.employee_two).delete()

    def test_create_sales_rep(self):
        obj = SalesRepresentative.objects.create(
            employee=self.employee_two
        )
        self.assertIsInstance(obj, SalesRepresentative)

    def test_sales_total(self):
        rep = SalesRepresentative.objects.create(
            employee=self.employee_two
        )
        inv = SalesInvoice.objects.create(
            status='paid',
            customer=self.customer_org,
            salesperson=rep
            )
        SalesInvoiceLine.objects.create(
            product=self.product,
            quantity=1,
            invoice=inv
        )
        
        self.assertEqual(rep.sales(TODAY, TODAY), 10)

class CreditNoteModelTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json','invoicing.json']

    @classmethod
    def setUpTestData(cls):
        create_test_inventory_models(cls)
        create_test_invoicing_models(cls)
        cls.inv = SalesInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
            salesperson=SalesRepresentative.objects.first()
            )
        SalesInvoiceLine.objects.create(
            product=cls.product,
            quantity=2,
            invoice=cls.inv,
            returned_quantity=1
        )

        cls.note = CreditNote.objects.create(
            date=TODAY,
            invoice=cls.inv,
            comments="Test comment"
        )
    
    def test_create_credit_note(self):
        inv = SalesInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
            salesperson=SalesRepresentative.objects.first()
            )

        obj = CreditNote.objects.create(
            date=TODAY,
            invoice=inv,
            comments="return processed for defective units"
        )
        self.assertIsInstance(obj, CreditNote)

    def test_returned_products(self):
        self.assertEqual(self.note.returned_products.count(), 1)


    def test_returned_total(self):
        self.assertEqual(self.note.returned_total, 10)


    def test_create_entry(self):
        self.note.create_entry()
        self.assertEqual(self.note.invoice.customer.account.balance, 10)


# The abstract sale object will be tested via tests to the sales invoice
# object.

class SalesInvoiceTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json','invoicing.json', 'settings.json']
    
    @classmethod
    def setUpTestData(cls):
        create_test_inventory_models(cls)
        create_test_invoicing_models(cls)
        cls.inv = SalesInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
            )
        cls.line = SalesInvoiceLine.objects.create(
            product=cls.product,
            quantity=1,
            invoice=cls.inv,
        )
    

    def test_create_sales_invoice(self):
        obj = SalesInvoice.objects.create(
            status="invoice",
            customer=self.customer_org,
            salesperson=SalesRepresentative.objects.first(),
            date=TODAY,
            due=TODAY,
            discount=0,
            tax=Tax.objects.first(),
            terms="test terms",
            comments="test comments",
            purchase_order_number='100',
            ship_from=self.warehouse
        )
        self.assertIsInstance(obj, SalesInvoice)

    def test_overdue(self):
        self.assertFalse(self.inv.overdue)
        self.inv.due = TODAY - datetime.timedelta(days=1)
        self.inv.save()
        self.assertTrue(self.inv.overdue)
        # rollback
        self.inv.due= TODAY
        self.inv.save()

    def test_abstract_filter(self):
        invs = AbstractSale.abstract_filter(Q(date=TODAY))
        self.assertEqual(len([i for i in invs]), 1)

    def test_set_quote_invoice_number(self):
        old_status = self.inv.status
        self.inv.status = 'quotation'
        self.inv.save()
        self.inv.set_quote_invoice_number()
        self.assertEqual(self.inv.quotation_number, 1)
        self.inv.status = old_status
        self.inv.save()
        self.inv.set_quote_invoice_number()
        self.assertEqual(self.inv.invoice_number, 1)

    def test_subtotal(self): 
        self.assertEqual(self.inv.subtotal, 10)

    def test_total(self):
        self.inv.tax = Tax.objects.latest('pk')#10 % tax 
        self.inv.save()
        self.assertEqual(self.inv.total, D('11.0'))
        self.inv.tax = None 
        self.inv.save()

    def test_on_credit(self):
        self.assertFalse(self.inv.on_credit)
        self.inv.due = TODAY - datetime.timedelta(days=1)
        self.inv.status = 'invoice'
        self.inv.save()
        self.assertTrue(self.inv.on_credit)
        self.inv.due = TODAY
        self.inv.save()

    def test_total_paid(self):
        self.assertEqual(self.inv.total_paid, 0)
        pmt = Payment.objects.create(
            payment_for=0,
            sales_invoice=self.inv,
            amount=10,
            date=TODAY,
            sales_rep=SalesRepresentative.objects.first()
        )
        self.assertEqual(self.inv.total_paid, 10) 
        pmt.delete()       

    def test_total_due(self):
        self.assertEqual(self.inv.total_due, 10)

    def test_tax_amount(self):
        self.inv.tax = Tax.objects.latest('pk')
        self.inv.save()
        self.assertEqual(self.inv.tax_amount, D('1.00'))

    def test_subtotal(self):
        self.assertEqual(self.inv.subtotal, 10)

    def test_add_product(self):
        self.inv.add_product(self.product, 10)
        self.assertEqual(self.inv.subtotal, 110)
        #rollback
        SalesInvoiceLine.objects.latest('pk').delete()

    def test_returned_total(self):
        self.line.returned_quantity = 1
        self.line.save()
        self.assertEqual(self.inv.returned_total, 10)
        #rollback
        self.line.returned_quantity = 0
        self.line.save()

    def test_update_inventory(self):
        wh_item = WareHouseItem.objects.get(product=self.product)
        initial_quantity = wh_item.quantity
        self.inv.update_inventory()
        wh_item = WareHouseItem.objects.get(product=self.product)
        self.assertEqual(wh_item.quantity, initial_quantity - 1)
        wh_item.quantity = 10
        wh_item.save()

    def test_create_entry(self):
        self.inv.create_entry()
        self.assertIsInstance(self.inv.entry, JournalEntry)
        #rollback
        self.inv.status = "invoice"
        self.inv.save()

    def test_create_sales_invoice_line(self):
        obj = SalesInvoiceLine.objects.create(
            invoice=self.inv,
            product=self.product,
            quantity=1,
        )
        self.assertIsInstance(obj, SalesInvoiceLine)
        obj.delete()

    def test_return_invoice_line_line(self):
        self.line._return(1)
        self.assertEqual(self.line.returned_quantity, 1)
        #rollback 
        self.line.returned_quantity = 0
        self.line.save()

    def test_returned_value(self):
        self.line._return(1)
        self.assertEqual(self.line.returned_value, D('10'))

class BillTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json',
        'invoicing.json',  'journals.json','settings.json']
    
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        cls.inv = Bill.objects.create(
            customer_reference="100",
            status='invoice',
            customer=cls.customer_org,
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
        cls.line = BillLine.objects.create(
            bill=cls.inv,
            expense=cls.exp
            )

    def test_create_bill(self):
        obj = Bill.objects.create(
            customer_reference="100",
            status='invoice',
            customer=self.customer_org,
        )
        self.assertIsInstance(obj, Bill)


    def test_get_billable_expenses(self):
        self.assertEqual(self.inv.billable_expenses.count(), 0)
        exp = Expense.objects.create(
            date=TODAY,
            billable=True,
            customer=self.customer_org,
            amount=10,
            description="test description",
            category=0,
            debit_account=Account.objects.first()
        )
        self.assertEqual(self.inv.billable_expenses.count(), 1)
        exp.delete()

    def test_add_line(self):
        self.assertEqual(self.inv.billline_set.count(), 1)
        self.inv.add_line(Expense.objects.first().pk)
        self.assertEqual(self.inv.billline_set.count(), 2)
        BillLine.objects.latest('pk').delete()

    def test_subtotal(self):
        self.assertEqual(self.inv.subtotal, 10)

    def test_total(self):
        self.assertEqual(self.inv.total, 10)

    def test_create_entry(self):
        pre_balance = Account.objects.get(name='Advertising').balance
        self.inv.create_entry()
        self.assertEqual(
            Account.objects.get(name='Advertising').balance,
            pre_balance + 10)

    def test_create_bill_line(self):
        obj = BillLine.objects.create(
            bill=self.inv,
            expense=self.exp
        )

class ServiceInvoiceModelTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json','invoicing.json', 'settings.json']
    
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        cls.inv = ServiceInvoice.objects.create(
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
        cls.line = ServiceInvoiceLine.objects.create(
            invoice=cls.inv,
            service=cls.service,
            hours=0
        )
        
    def test_create_service_invoice(self):
        obj = ServiceInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
        )
        self.assertIsInstance(obj, ServiceInvoice)

    def test_subtotal(self):
        self.assertEqual(self.inv.subtotal, 10)
    
    def test_add_line(self):
        self.inv.add_line(Service.objects.first().pk, 1)
        #line one = 10 + line 2 = (10 + 1) total = 21
        self.assertEqual(self.inv.subtotal, 21)
    
    def test_create_service_invoice_line(self):
        obj = ServiceInvoiceLine.objects.create(
            invoice=self.inv,
            service=self.service,
            hours=0
        )
        self.assertIsInstance(obj, ServiceInvoiceLine)

    def test_service_invoice_line_total(self):
        self.assertEqual(self.line.total, 10)


class CombinedInvoiceModelTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json','invoicing.json', 'settings.json', 'journals.json']
    
    @classmethod
    def setUpTestData(cls):
        create_test_invoicing_models(cls)
        create_test_inventory_models(cls)
        cls.inv = CombinedInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
        )
        cat = ServiceCategory.objects.create(
            name="name"
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
        cls.service = Service.objects.create(
            name="Test Service",
            description="some description",
            flat_fee=10,
            hourly_rate=1,
            frequency="once",
            category=cat
        )
        cls.line_sale = CombinedInvoiceLine.objects.create(
            invoice=cls.inv,
            product=cls.product,
            line_type=1,
            quantity_or_hours=1
        )
        cls.line_service = CombinedInvoiceLine.objects.create(
            invoice=cls.inv,
            service=cls.service,
            line_type=2,
            quantity_or_hours=0
        )
        cls.line_bill = CombinedInvoiceLine.objects.create(
            invoice=cls.inv,
            expense=cls.exp,
            line_type=3,
            quantity_or_hours=0
        )

    def test_create_combined_invoice(self):
        obj = CombinedInvoice.objects.create(
            status='invoice',
            customer=self.customer_org,
        )

    def test_add_product_line(self):
        pre_total = self.inv.subtotal
        self.inv.add_line({
            'lineType': 'sale',
            'data':{
                'item': '1-name',
                'quantity': 1
            }
        })
        self.assertEqual(self.inv.total, pre_total + 10)

    def test_add_service_line(self):
        pre_total = self.inv.subtotal
        self.inv.add_line({
            'lineType': 'service',
            'data':{
                'service': '1-name',
                'hours': 0
            }
        })
        self.assertEqual(self.inv.total, pre_total + 10)

    def test_add_billable_line(self):
        pre_total = self.inv.subtotal
        self.inv.add_line({
            'lineType': 'billable',
            'data':{
                'billable': '1-name',
                'hours': 0
            }
        })
        added = Expense.objects.get(pk=1).amount
        self.assertEqual(self.inv.total, pre_total + added)

    def test_subtotal(self):
        self.assertEqual(self.inv.subtotal, 30)

    def test_line_subtotal(self):
        self.assertEqual(self.line_sale.subtotal, 10)
        self.assertEqual(self.line_service.subtotal, 10)
        self.assertEqual(self.line_bill.subtotal, 10)
