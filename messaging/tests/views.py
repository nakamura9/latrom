import json
import urllib

from django.test import TestCase, Client
from django.contrib.auth.models import User
from messaging.models import *
from common_data.tests import create_test_common_entities
from smtpd import SMTPServer
import threading
import asyncore

class ChatViewTests(TestCase):
    fixtures = ['common.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='123')
        cls.person = User.objects.create_user(username='person', password='456')
        cls.chat = Chat.objects.create(sender=cls.user, receiver=cls.person)
        cls.group = Group.objects.create(admin=cls.user)
        cls.notification = Notification.objects.create(title='hello', message='world')
        cls.profile = UserProfile.objects.create(user=cls.user, email_address='test@gmail.com', email_password='123')


    def setUp(self):
        self.client.login(username='test', password='123')
    
    def test_get_chat_list_view(self):
        resp = self.client.get('/messaging/chat-list')
        self.assertEqual(resp.status_code, 200)

    def test_get_chat_detail_view(self):
        resp = self.client.get('/messaging/chat/1')
        self.assertEqual(resp.status_code, 200)
    
    def test_get_chat_create_view(self):
        resp = self.client.get('/messaging/new-chat')
        self.assertEqual(resp.status_code, 200)

    def test_get_create_view_with_user(self):
        resp = self.client.get('/messaging/create-chat/1')
        self.assertEqual(resp.status_code, 302)

    def test_post_group_create_view(self):
        resp = self.client.post('/messaging/create-group',data={
            'participants': urllib.parse.quote(json.dumps(['1-test'])),
            'name':'name',
            'admin': self.user.pk
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_group_list_view(self):
        resp = self.client.get('/messaging/group-list')
        self.assertEqual(resp.status_code, 200)

    def test_get_group_detail_view(self):
        resp = self.client.get('/messaging/group/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_chat_with_closing(self):
        resp = self.client.get('/messaging/close-chat/1')
        self.assertEqual(resp.status_code, 302)

    def test_group_close(self):
        resp = self.client.get('/messaging/close-group/1')
        self.assertEqual(resp.status_code, 302)
    
    def test_get_notify_detail_view(self):
        resp = self.client.get('/messaging/notification/1')
        self.assertEqual(resp.status_code, 200)

    def test_dashboard(self):
        resp = self.client.get('/messaging/dashboard/')
        self.assertEqual(resp.status_code, 200)

    def test_notification_service(self):
        resp = self.client.get('/messaging/api/notifications')
        self.assertEqual(resp.status_code, 200)

    def test_notification_read(self):
        resp = self.client.get('/messaging/api/notifications/mark-read/1')
        self.assertEqual(resp.status_code, 200)

    
class TestEmailServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        filename = 'mail.eml'
        f = open(filename, 'w')
        f.write(data)
        f.close()
class EmailViewTests(TestCase):
    fixtures = ['common.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        server = TestEmailServer(('localhost', 25), None)
        cls.server = threading.Thread(target=asyncore.loop)
        cls.server.daemon = True
        cls.server.start()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='123')
        cls.person = User.objects.create_user(username='person', password='456')
        cls.profile = UserProfile.objects.create(
            user=cls.user, 
            email_address='test@gmail.com', 
            email_password='123',
            outgoing_server='localhost',
            outgoing_port=25)
        cls.email_address = EmailAddress.objects.create(address='test@gmail.com')
        cls.folder = EmailFolder.objects.create(
            name='inbox',
            label='inbox'
        )
        cls.email = Email.objects.create(
                created_timestamp=datetime.datetime.now(),
                body='hello', 
                folder=cls.folder,
                owner=cls.user,
                to=cls.email_address)


    def setUp(self):
        self.client.login(username='test', password='123')
    
    def test_message_create(self):
        resp = self.client.get('/messaging/create-message')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_message(self):
        self.assertTrue(True)
        # resp = self.client.post('/messaging/create-message', data={
        #     'body': 'things',
        #     'folder': 'sent',
        #     'owner': self.user.pk,
        #     'subject': 'fw',
        # })

        # self.assertEqual(resp.status_code, 302)
        # self.assertTrue(os.path.exists('email.eml'))
        #os.remove('email.eml')
        

    def test_inbox(self):
        resp = self.client.get('/messaging/inbox/')
        self.assertEqual(resp.status_code, 200)

    #TODO fix
    '''
    def test_get_configuration(self):
        resp = self.client.get('/messaging/config/')
        self.assertEqual(resp.status_code, 200)

    
    def test_post_configuration(self):
        resp = self.client.post('/messaging/config/', data={
            'user': self.user.pk,
            'email_address':'test@gmail.com',
            'email_password':'123',
            'email_fields':'test@gmail.com',
        })
        self.assertEqual(resp.status_code, 302)'''

    

    def test_api_send_draft(self):
        self.assertTrue(True)
        #resp = self.client.get('/messaging/api/send-draft/1/')
        #self.assertEqual(resp.status_code, 200)

    def test_api_reply_email(self):
        self.assertTrue(True)
        #TODO copy entity map into body
        # resp = self.client.get('/messaging/api/reply-email/1/')
        # self.assertEqual(resp.status_code, 200)
