from django.urls import path
from inventory import views
incoming_urls = [
    path('incoming/orders/<int:pk>', views.IncomingOrderListView.as_view(), 
        name='incoming-orders'),
    path('incoming/transfers/receipts-list/<int:pk>', 
        views.TransferOrderReceiptsList.as_view(), 
        name='incoming-transfers-receipts-list'),
    path('incoming/credit-notes/list/<int:pk>', 
        views.IncomingReturnsListView.as_view(), 
        name='incoming-credit-notes-list'),
    path('incoming/receive-returns/<int:pk>', 
        views.CreditNoteStockReceiptCreateView.as_view(), 
        name='incoming-receive-returns'),
    path('incoming/credit-note/returned/<int:pk>', 
        views.SingleSalesReturnListView.as_view(), 
        name='incoming-credit-note-returned'),
]