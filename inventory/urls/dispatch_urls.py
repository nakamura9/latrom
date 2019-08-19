from django.urls import path
from inventory.views import (PurchaseReturnListView, 
                             DeliveryNoteView, 
                             DispatchPurchaseReturnsView,
                             InvoiceDispatchListView,
                             DispatchInvoiceView)
dispatch_urls = [
    path('dispatch/debit-notes/list/<int:warehouse>', 
        PurchaseReturnListView.as_view(), name='dispatch-debit-note-list'),
    path('dispatch/delivery-note/<int:pk>', DeliveryNoteView.as_view(), 
        name='delivery-note'),
    path('dispatch/purchase-returns/<int:debit_note>', 
        DispatchPurchaseReturnsView.as_view(), 
        name='dispatch-purchase-returns'),
    path('dispatch/invoice/<int:invoice>', 
        DispatchInvoiceView.as_view(), 
        name='dispatch-invoice'),
    path('dispatch/invoices/list/<int:warehouse>', 
        InvoiceDispatchListView.as_view(), name='dispatch-invoice-list'),
]