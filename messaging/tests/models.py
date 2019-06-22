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
        obj = Chat.objects.create(
            sender=self.usr,
            receiver=self.receiver
        )
        self.assertIsInstance(obj, Chat)

    def test_user_chats(self):
        self.assertTrue(Chat.user_chats(self.usr).count() > 0)

    def test_chat_messages(self):
        bubble = Bubble.objects.create(
            sender=self.usr,
            message_text = 'Hello world',
            chat=self.chat
        )

        self.assertEqual(self.chat.messages.first().pk, bubble.pk)

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
        cls.group.participants.add(cls.usr)
        cls.group.participants.add(cls.receiver)

        
    def setUp(self):
        pass

    def test_create_group(self):
        obj = Group.objects.create(
            admin=self.usr,
            name='Group B'
        )

        self.assertIsInstance(obj, Group)

    def test_group_messages(self):
        bubble = Bubble.objects.create(
            sender=self.usr,
            message_text = 'Hello world',
            group=self.group
        )

        self.assertEqual(self.group.messages.first().pk, bubble.pk)

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

        cls.group = Group.objects.create(
            admin=cls.usr,
        )

        cls.bubble = Bubble.objects.create(
            sender=cls.usr,
            message_text = "Hi",
            chat=cls.chat,
        )

    def test_create_chat_bubble(self):
        obj = Bubble.objects.create(
            sender=self.usr,
            message_text = "Hi",
            chat=self.chat,
        )

        self.assertIsInstance(obj, Bubble)


    def test_create_group_bubble(self):
        obj = Bubble.objects.create(
            sender=self.usr,
            message_text = "Hi",
            group=self.group,
        )

        self.assertIsInstance(obj, Bubble)

class EmailTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="someone")
        cls.from_address = EmailAddress.objects.create(address='test@email.com')
        cls.to_address = EmailAddress.objects.create(address='to@email.com')

        cls.profile = UserProfile.objects.create(
            user=cls.usr,
            email_address='test@email.com',
            email_password='gibberish',
        )

        cls.email = Email.objects.create(
            created_timestamp=datetime.datetime.now(),
            sent_from=cls.from_address,
            to=cls.to_address,
            server_id='1',
            body='<p>Hello world</p>',
            subject='subject',
        )

    def test_create_email_address(self):
        obj = EmailAddress.objects.create(address='email@address.com')
        self.assertIsInstance(obj, EmailAddress)
        

    def test_create_user_profile(self):
        self.assertIsInstance(self.profile, UserProfile)

    def test_create_email(self):
        obj= Email.objects.create(
            sent_from=self.from_address,
            to=self.to_address,
            created_timestamp=datetime.datetime.now(),
            server_id='123',
            body='<p>Hello world</p>',
            subject='subject',
        )
        self.assertIsInstance(obj, Email)

    def test_get_email_address_existing(self):
        self.assertIsInstance(
            EmailAddress.get_address('test@email.com'), 
            EmailAddress)

    def test_get_email_address_new(self):
        self.assertIsInstance(
            EmailAddress.get_address('test99@email.com'), 
            EmailAddress)