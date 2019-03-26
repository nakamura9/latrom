import invoicing

class InvoiceCreateMixin(object):
    payment = None
    payment_for = 0 #customize for each type
    def get_initial(self):
        config = invoicing.models.SalesConfig.objects.first()
        if self.kwargs.get('customer', None):
            return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments,
            'customer': self.kwargs['customer']
        }

        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    