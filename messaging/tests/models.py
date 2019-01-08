import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from messaging.models import *


TODAY = datetime.date.today()

class DispatcherTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.sender = User.objects.create_user(username="someone")
        cls.copied = User.objects.create_user(username="somethree")
        cls.receiver = User.objects.create_user(username="sometwo")
        
        cls.message = Message.objects.create(
            recipient=cls.receiver,
            sender=cls.sender,
            subject='subject',
            body='body',
        )
        cls.message.copy.set(User.objects.filter(username='somethree'))

        cls.dispatcher = Dispatcher(cls.message)
    
    def setUp(self):
        pass

    def test_create_dispatcher(self):
        obj = Dispatcher(self.message)
        self.assertIsInstance(obj, Dispatcher)

    def dispatcher_get_inbox(self):
        obj = self.dispatcher.get_inbox(self.sender)
        self.assertIsInstance(obj, Inbox)
        self.assertEqual(obj.user, self.user)

    def test_user_has_inbox(self):
        self.assertFalse(self.dispatcher.has_inbox(self.receiver))

    def test_dispatch_message(self):
        self.dispatcher.dispatch()
        print(MessageThread.objects.all().count())
        self.assertEqual(self.receiver.inbox.threads.all().count(), 1)
        self.assertEqual(self.copied.inbox.threads.all().count(), 1)