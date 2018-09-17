from django.db import models
from common_data.models import SingletonModel

from .invoices import *
from .customer import Customer
from .payment import Payment
from .sales_rep import SalesRepresentative
from .credit_note import CreditNote


class SalesConfig(SingletonModel):
    DOCUMENT_THEME_CHOICES = [
        (1, 'Simple'),
        (2, 'Blue'),
        (3, 'Steel'),
        (4, 'Verdant'),
        (5, 'Warm')
    ]
    CURRENCY_CHOICES = [
        ('$', 'Dollars($)'), 
        ('R', 'Rand')
    ]

    default_invoice_comments = models.TextField(blank=True)
    default_quotation_comments = models.TextField(blank=True)
    default_credit_note_comments = models.TextField(blank=True)
    default_terms = models.TextField(blank=True)
    sales_tax = models.ForeignKey('accounting.Tax', on_delete=None, null=True, blank="True")
    include_shipping_address = models.BooleanField(default=False)
    business_address = models.TextField(blank=True)
    logo = models.ImageField(null=True,upload_to="logo/")
    document_theme = models.IntegerField(choices= DOCUMENT_THEME_CHOICES)
    currency = models.CharField(max_length=1, choices=CURRENCY_CHOICES)
    apply_price_multiplier = models.BooleanField(default=False)
    price_multiplier =models.FloatField(default=0.0)
    business_name = models.CharField(max_length=255)
    payment_details = models.TextField(blank=True)
    contact_details = models.TextField(blank=True)
    include_tax_in_invoice = models.BooleanField(default=True)
    include_units_in_sales_invoice = models.BooleanField(default=True)
    business_registration_number = models.CharField(max_length=32,blank=True)

    @classmethod
    def get_config_dict(cls):
        d = cls.objects.first().__dict__
        del d['_state']
        return d

    @classmethod
    def logo_url(cls):
        conf = cls.objects.first()
        if conf.logo:
            return conf.logo.url
        return ""