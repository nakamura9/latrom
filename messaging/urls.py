from django.urls import path, re_path
from messaging import views
app_name = 'messaging'

urlpatterns = [
    path('message-detail/<int:pk>', views.MessageDetailView.as_view(), 
        name='message-detail'),
    path('inbox/<int:pk>', views.InboxView.as_view(), name='inbox'),
    path('notification/<int:pk>', views.NotificationDetailView.as_view(), 
        name='notification'),
    path('create-message', views.ComposeMessageView.as_view(), 
        name='create-message'),
    path('message-thread/<int:pk>', views.MessageThreadView.as_view(),
        name='message-thread'),
    path('reply-message/<int:pk>', views.reply_message,
        name='reply-message'),
    path('inbox-counter/', views.inbox_counter,
        name='inbox-counter')
]