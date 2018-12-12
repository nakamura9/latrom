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

    def form_valid(self, form):
        '''initially set the amount to zero until the post method sets the actual value of the payment'''
        resp =  super().form_valid(form)
        #from the checkbox
        if form.cleaned_data['apply_payment']:
            payment_data = {
                'payment_for': self.payment_for,
                'amount':0,
                'date':self.object.due,
                'sales_rep':self.object.salesperson
            }

            mapping = {
                0: {'sales_invoice': self.object},
                1: {'service_invoice': self.object},
                2: {'bill': self.object},
                3: {'combined_invoice': self.object},

            }

            payment_data.update(mapping[self.payment_for])

            self.payment = invoicing.models.Payment.objects.create(
                **payment_data)
                
            self.object.status = 'paid'
            self.object.save()

        return resp

    def set_payment_amount(self):
        if self.payment:
            self.payment.amount = self.object.total
            self.payment.save()
            self.payment.create_entry()