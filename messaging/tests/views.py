import json

from django.test import TestCase, Client
from django.contrib.auth.models import User
from messaging.models import *
from common_data.tests import create_test_common_entities


class MessagingViewTests(TestCase):
    fixtures = ['common.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        
    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_superuser('User', 'abc@xyz.com', '123')
        cls.receiver = User.objects.create_user(username="sometwo")
        create_test_common_entities(cls)
        
        cls.message = Message.objects.create(
            recipient=cls.receiver,
            sender=cls.usr,
            subject='subject',
            body='body',
        )
        cls.notification = Notification.objects.create(
            user=cls.usr,
            title='Title',
            message="Message"
        )

    def setUp(self):
        self.client.login(username='User', password='123')

    def test_get_inbox(self):
        resp = self.client.get('/messaging/inbox/')
        self.assertEqual(resp.status_code, 200)

    def test_get_dashboard(self):
        resp = self.client.get('/messaging/dashboard/')
        self.assertEqual(resp.status_code, 200)

    def test_get_message_detail_page(self):
        resp = self.client.get('/messaging/message-detail/1')
        self.assertEqual(resp.status_code, 200)


    def test_get_message_compose_page(self):
        resp = self.client.get('/messaging/create-message')
        self.assertEqual(resp.status_code, 200)

    def test_post_message_compose_view(self):
        resp = self.client.post('/messaging/create-message', data={
            'copy': [],
            'recipient': 1,
            'subject': 'sub',
            'body': 'body',
            'sender': 1
        })

        self.assertEqual(resp.status_code, 302)

    def test_get_notification_detail_page(self):
        resp = self.client.get('/messaging/notification/1')

    def test_get_notification_service(self):
        resp = self.client.get('/messaging/api/notifications')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['unread'], 0)

    def test_get_notification_service(self):
        obj = Notification.objects.create(
            user=self.usr, 
            title='title',
            message= 'message')
        resp = self.client.get('/messaging/api/notifications')
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['unread'], 2)

        obj.delete()

    def test_mark_notification_read(self):
        obj = Notification.objects.create(
            user=self.usr, 
            title='title',
            message= 'message')
        resp = self.client.get('/messaging/api/notifications/mark-read/' + \
            str(obj.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Notification.objects.get(pk=obj.pk).read)

        obj.delete()

class MessagingAPIViewTests(TestCase):
    fixtures = ['common.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        
    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_superuser('User', 'abc@xyz.com', '123')
        cls.receiver = User.objects.create_user(username="sometwo")
        create_test_common_entities(cls)
        
        cls.message = Message.objects.create(
            recipient=cls.receiver,
            sender=cls.usr,
            subject='subject',
            body='body',
        )
        cls.notification = Notification.objects.create(
            user=cls.usr,
            title='Title',
            message="Message"
        )

        cls.thread = MessageThread.objects.create(
            initiator=cls.usr
        )

        cls.inbox = Inbox.objects.create(
            user=cls.usr
        )

    def setUp(self):
        self.client.login(username='User', password='123')
    
    def test_reply_message(self):
        resp = self.client.post('/messaging/reply-message/1', data={
            'reply': 'Test Reply'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Message.objects.all().count(), 2)

    def test_inbox_counter(self):
        resp = self.client.get('/messaging/inbox-counter/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['count'], 1)

    def test_mark_as_read(self):
        resp = self.client.get('/messaging/api/mark-as-read/1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Message.objects.first().read)

    def test_close_thread(self):
        resp = self.client.get('/messaging/api/close-thread/1')
        self.assertTrue(MessageThread.objects.first().closed)
        self.assertEqual(resp.status_code, 302)

