from django.urls import path, re_path
from messaging import views
app_name = 'messaging'
from rest_framework.routers import DefaultRouter

chat_router = DefaultRouter()
chat_router.register(r'^api/chat', views.ChatAPIViewset)

group_router = DefaultRouter()
group_router.register(r'^api/group', views.GroupAPIViewset)

bubble_router = DefaultRouter()
bubble_router.register(r'^api/bubble', views.BubbleAPIViewset)

chat_urls = [
    path('chat-list', views.ChatListView.as_view(), name='chat-list'),
    path('chat/<int:pk>', views.ChatView.as_view(), name='chat'),
    path('new-chat', views.NewChatView.as_view(), name='new-chat'),
    path('create-chat/<int:user>', views.create_chat, name='create-chat'),
    path('create-group', views.GroupCreateView.as_view(), name='create-group'),
    path('group-list', views.GroupListView.as_view(), name='group-list'),
    path('group/<int:pk>', views.GroupView.as_view(), name='group')
] + chat_router.urls + bubble_router.urls  + group_router.urls

urlpatterns = [
    path('message-detail/<int:pk>', views.MessageDetailView.as_view(), 
        name='message-detail'),
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('notification/<int:pk>', views.NotificationDetailView.as_view(), 
        name='notification'),
    path('create-message', views.ComposeMessageView.as_view(), 
        name='create-message'),
    path('reply-message/<int:pk>', views.reply_message,
        name='reply-message'),
    path('inbox-counter/', views.inbox_counter,
        name='inbox-counter'),
    path('api/message-thread/<int:pk>', views.MessageThreadAPIView.as_view(),
        name='api-message-thread'),
    path('api/message/<int:pk>', views.MessageAPIView.as_view(),
        name='api-message'),
    path('api/mark-as-read/<int:pk>', views.mark_as_read,
        name='api-mark-as-read'),
    path('api/close-thread/<int:pk>', views.close_thread,
        name='api-close-thread'),
    path('api/notifications', views.notification_service,
        name='api-notifications'),
    path('api/notifications/mark-read/<int:pk>', views.mark_notification_read,
        name='api-notifications-mark-read'),
] + chat_urls