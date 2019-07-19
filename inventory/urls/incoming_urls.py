from django.urls import path
from inventory import views
incoming_urls = [
    path('incoming/orders/<int:pk>', views.IncomingOrderListView.as_view(), name='incoming-orders')
]