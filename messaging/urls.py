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

email_router = DefaultRouter()
email_router.register(r'^api/email', views.EmailAPIViewset)

email_address_router = DefaultRouter()
email_router.register(r'^api/email-address', views.EmailAddressAPIViewset)

email_folder_router = DefaultRouter()
email_router.register(r'^api/email-folder', views.EmailFolderAPIViewset)

profile_router = DefaultRouter()
profile_router.register(r'^api/email-profile', views.UserProfileAPIViewset)


chat_urls = [
    path('chat-list', views.ChatListView.as_view(), name='chat-list'),
    path('chat/<int:pk>', views.ChatView.as_view(), name='chat'),
    path('new-chat', views.NewChatView.as_view(), name='new-chat'),
    path('create-chat/<int:user>', views.create_chat, name='create-chat'),
    path('create-group', views.GroupCreateView.as_view(), name='create-group'),
    path('group-list', views.GroupListView.as_view(), name='group-list'),
    path('group/<int:pk>', views.GroupView.as_view(), name='group'),
    path('close-chat/<int:pk>', views.close_chat, name='close-chat'),
    path('close-group/<int:pk>', views.close_group, name='close-group'),
    path('api/chat/get-latest/<int:chat>', views.get_latest_chat_messages, 
        name='chat-api-get-latest'),
    path('api/group/get-latest/<int:group>', views.get_latest_group_messages, 
        name='group-api-get-latest'),
    path('api/delete-messages/', views.delete_messages, name='api/delete-messages'),
    path('api/forward-messages/<int:user>', views.forward_messages, name='api/forward-messages'),
    path('api/sync-folders/<int:profile_id>/', views.sync_folders)

] + chat_router.urls + bubble_router.urls  + group_router.urls + \
        email_router.urls + email_address_router.urls

email_urls = [
    path('create-message', views.ComposeEmailView.as_view(), 
        name='create-message'),
    path('create-email-address', views.EmailAddressCreateView.as_view(), 
        name='create-email-address'),
    path('email/update-draft/<int:pk>', views.DraftEmailUpdateView.as_view(), 
        name='email-update-draft'),
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('config/', views.UserProfileView.as_view(), name='config'),
    path("api/folder/<int:folder>", views.FolderAPIView.as_view(), name="inbox-api"),
    path("api/send-draft/<int:pk>/", views.send_draft, name='send-draft'),
    path("api/reply-email/<int:pk>/", views.reply_email, name='reply-email'),
    path("api/add-group-participant/<int:grp>/<int:id>", views.add_participant, 
        name='add-group-participant'),
    path("api/remove-group-participant/<int:grp>/<int:id>",     
        views.remove_participant, name='remove-group-participant'),
    path("api/forward-email/<int:pk>", views.forward_email_messages, 
        name='forward-email'),
]

urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('user-icon/', views.get_user_icon, name='user-icon'),
    path('notification/<int:pk>', views.NotificationDetailView.as_view(), 
        name='notification'),    
    path('api/notifications', views.notification_service,
        name='api-notifications'),
    path('api/notifications/mark-read/<int:pk>', views.mark_notification_read,
        name='api-notifications-mark-read'),
] + chat_urls + email_urls +email_folder_router.urls + \
    profile_router.urls