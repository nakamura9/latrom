import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from messaging.models import *


TODAY = datetime.date.today()
class NotificationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="someone")
        cls.notification = Notification.objects.create(
            user=cls.usr,
            title='Title',
            message="Message"
        )
    def setUp(self):
        pass

    def test_create_notification(self):
        obj = Notification.objects.create(
            user=self.usr,
            title='Title',
            message="Message"
        )

        self.assertIsInstance(obj, Notification)

    def test_open_notification(self):
        self.assertFalse(self.notification.read)
        self.notification.open()
        self.assertTrue(self.notification.read)



class ChatTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="someone")
        cls.receiver = User.objects.create_user(username="sometwo")

        cls.chat = Chat.objects.create(
            sender=cls.usr,
            receiver=cls.receiver
        )
        
    def setUp(self):
        pass

    def test_create_chat(self):
        self.assertTrue(False)

    def test_user_chats(self):
        self.assertTrue(False)

class GroupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="someone")
        cls.receiver = User.objects.create_user(username="sometwo")

        cls.group = Group.objects.create(
            admin=cls.usr,
        )
        cls.group.participants.add([cls.usr, cls.receiver])
        
    def setUp(self):
        pass

    def test_create_group(self):
        self.assertTrue(False)

class BubbleTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="someone")
        cls.receiver = User.objects.create_user(username="sometwo")

        cls.chat = Chat.objects.create(
            sender=cls.usr,
            receiver=cls.receiver
        )

        cls.bubble = Bubble.objects.create(
            sender=cls.usr,
            message_text = "Hi",
            chat=cls.chat,
        )

        def test_create_chat_bubble(self):
            self.assertTrue(False)

        def test_create_group_bubble(self):
            self.assertTrue(False)