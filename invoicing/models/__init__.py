from django.db import models
from common_data.models import SingletonModel

from .invoice import *
from .customer import Customer
from .payment import Payment
from .sales_rep import SalesRepresentative
from .credit_note import CreditNote, CreditNoteLine


class SalesConfig(SingletonModel):
    default_invoice_comments = models.TextField(blank=True)
    default_quotation_comments = models.TextField(blank=True)
    default_credit_note_comments = models.TextField(blank=True)
    default_terms = models.TextField(blank=True)
    sales_tax = models.ForeignKey('accounting.Tax', on_delete=models.SET_NULL,  
        null=True, blank="True")
    include_shipping_address = models.BooleanField(default=False)
    include_tax_in_invoice = models.BooleanField(default=True)
    include_units_in_sales_invoice = models.BooleanField(default=True)
    next_invoice_number = models.IntegerField(default=1)
    next_quotation_number = models.IntegerField(default=1)
    use_sales_invoice = models.BooleanField(default=True)
    use_service_invoice = models.BooleanField(default=True)
    use_bill_invoice = models.BooleanField(default=True)
    use_combined_invoice = models.BooleanField(default=True)
    is_configured = models.BooleanField(default=False)


    @classmethod
    def get_config_dict(cls):
        d = cls.objects.first().__dict__
        del d['_state']
        return d

    