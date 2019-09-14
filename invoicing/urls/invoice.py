from django.urls import re_path, path
from rest_framework import routers

from invoicing import views

invoice_router = routers.DefaultRouter()
invoice_router.register('api/invoice', views.InvoiceAPIViewSet)

credit_note_urls = [
    re_path(r'^config-wizard', views.ConfigWizard.as_view(), name='config-wizard'),
    re_path(r'^credit-note-create/(?P<pk>[\w]+)/?$', 
        views.CreditNoteCreateView.as_view(), name='credit-note-create'),
    re_path(r'^credit-note-list/?$', views.CreditNoteListView.as_view(), 
        name='credit-note-list'),
    re_path(r'^credit-note-detail/(?P<pk>[\w]+)/?$', 
        views.CreditNoteDetailView.as_view(), name='credit-note-detail'),
    re_path(r'^credit-note-pdf/(?P<pk>[\w]+)/?$', 
        views.CreditNotePDFView.as_view(), name='credit-note-pdf'),
]

quotation_urls = [
    re_path(r'^create-quotation/?$', views.QuotationCreateView.as_view(), 
        name='create-quotation'),
    re_path(r'^(?P<customer>[\d]+)/create-quotation/?$', 
            views.QuotationCreateView.as_view(), name='create-quotation'),
    re_path(r'^quotation-detail/(?P<pk>[\d]+)/?$', 
            views.QuotaionDetailView.as_view(), name='quotation-details'),
    re_path(r'^quotation-update/(?P<pk>[\d]+)/?$', 
        views.QuotationUpdateView.as_view(), 
        name='quotation-update'),
    re_path(r'^quotation-pdf/(?P<pk>[\d]+)/?$', 
        views.QuotationPDFView.as_view(), 
        name='quotation-pdf'),
    re_path(r'^quotation-email/(?P<pk>[\d]+)/?$', 
        views.QuotationEmailSendView.as_view(), 
        name='quotation-email'),
    path('make-invoice/<int:pk>', views.make_invoice_from_quotation, 
        name='make-invoice'),
    path('make-proforma/<int:pk>', views.make_proforma_from_quotation, 
        name='make-proforma'),

]

urls = [
    re_path(r'^create-invoice/?$', views.InvoiceCreateView.as_view(), 
        name='create-invoice'),
    path('import-invoice-from-excel/', 
        views.ImportInvoiceFromExcelView.as_view(), 
        name='import-invoice-from-excel'),
    re_path(r'^(?P<customer>[\d]+)/create-invoice/?$', 
            views.InvoiceCreateView.as_view(), name='create-invoice'),
    re_path(r'^invoice-detail/(?P<pk>[\d]+)/?$', 
            views.InvoiceDetailView.as_view(), name='invoice-details'),
    re_path(r'^invoices-list/?$', views.InvoiceListView.as_view(), 
        name='invoices-list'),
    re_path(r'^invoice-update/(?P<pk>[\d]+)/?$', 
        views.InvoiceUpdateView.as_view(), 
        name='invoice-update'),
    re_path(r'^invoice-payment/(?P<pk>[\d]+)/?$', 
        views.InvoicePaymentView.as_view(), 
        name='invoice-payment'),
    re_path(r'^invoice-payment-detail/(?P<pk>[\d]+)/?$', 
        views.InvoicePaymentDetailView.as_view(), 
        name='invoice-payment-detail'),
    re_path(r'^invoice-pdf/(?P<pk>[\d]+)/?$', views.InvoicePDFView.as_view(), 
        name='invoice-pdf'),
    re_path(r'^invoice-email/(?P<pk>[\d]+)/?$', 
        views.InvoiceEmailSendView.as_view(), 
        name='invoice-email'),
    re_path(r'^invoice-payment-detail/(?P<pk>[\d]+)/?$', 
        views.InvoicePaymentDetailView.as_view(), 
        name='invoice-payment-detail'),
    re_path(r'^draft-delete/(?P<pk>[\d]+)/?$', 
        views.InvoiceDraftDeleteView.as_view(), name='draft-delete'),
    re_path(r'^invoice-returns/(?P<pk>[\d]+)/?$', 
        views.InvoiceReturnsDetailView.as_view(), 
        name='invoice-returns'),
    re_path(r'^invoice/verify/(?P<pk>[\d]+)/?$', 
        views.verify_invoice, 
        name='invoice-verify'),
    re_path(r'^invoice/shipping-costs/(?P<pk>[\d]+)/?$', 
        views.ShippingAndHandlingView.as_view(), 
        name='invoice-shipping-costs'),
    re_path(r'^invoice/shipping-costs/list/(?P<pk>[\d]+)/?$', 
        views.ShippingExpenseListView.as_view(), 
        name='invoice-shipping-costs-list'),
] + invoice_router.urls + credit_note_urls + quotation_urls
