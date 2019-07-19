from django.urls import path
from inventory.views import PurchaseReturnListView
dispatch_urls = [
    path('dispatch/debit-notes/list/<int:warehouse>', PurchaseReturnListView.as_view(), name='dispatch-debit-note-list')
]