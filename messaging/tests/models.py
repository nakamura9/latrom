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

    def test_dispatcher_get_inbox(self):
        obj = self.dispatcher.get_inbox(self.sender)
        self.assertIsInstance(obj, Inbox)

    def test_user_has_inbox(self):
        self.assertFalse(self.dispatcher.has_inbox(self.receiver))

    def test_dispatch_message(self):
        self.dispatcher.dispatch()
        self.assertEqual(self.receiver.inbox.threads.all().count(), 1)
        

class MessageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.sender = User.objects.create_user(username="someone")
        cls.receiver = User.objects.create_user(username="sometwo")
        
        cls.message = Message.objects.create(
            recipient=cls.receiver,
            sender=cls.sender,
            subject='subject',
            body='body',
        )
        cls.message.copy.set(User.objects.filter(username='somethree'))
        
    def setUp(self):
        pass

    def test_create_message(self):
        obj = Message.objects.create(
            recipient=self.receiver,
            sender=self.sender,
            subject='subject',
            body='body',
        )

        self.assertIsInstance(obj, Message)

    def test_message_is_reply(self):
        self.assertFalse(self.message.is_reply)
        thread = MessageThread.objects.create(
            initiator=self.sender
        )
        self.message.thread=thread
        self.message.save()
        self.assertTrue(self.message.is_reply)
        self.message.thread = None
        self.message.save()

    def test_open_message(self):
        self.message.open_message()
        self.assertTrue(self.message.read)
        self.assertIsNotNone(self.message.opened_timestamp)

        
class MessageThreadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.sender = User.objects.create_user(username="someone")
        cls.receiver = User.objects.create_user(username="sometwo")
        
        cls.message = Message.objects.create(
            recipient=cls.receiver,
            sender=cls.sender,
            subject='subject',
            body='body',
        )
        cls.thread = MessageThread.objects.create(
            initiator=cls.sender
        )

    def setUp(self):
        pass

    def test_create_thread(self):
        obj = MessageThread.objects.create(
            initiator=self.sender
        )
        self.assertIsInstance(obj, MessageThread)

    def test_thread_read_unread_messages(self):
        self.thread.messages.add(self.message)
        self.assertEqual(MessageThread.objects.first().unread.count(), 1)
        self.assertEqual(MessageThread.objects.first().read.count(), 0)
        
        self.message.read=True
        self.message.save()
        
        self.assertEqual(MessageThread.objects.first().unread.count(), 0)
        self.assertEqual(MessageThread.objects.first().read.count(), 1) 
        
        self.message.read=False
        self.message.save()

    def test_thread_add_message(self):
        msg = Message.objects.create(
            recipient=self.receiver,
            sender=self.sender,
            subject='subject',
            body='body',
        )
        prev_count = MessageThread.objects.first().messages.count()
        MessageThread.objects.first().add_message(msg)

        self.assertEqual(
            MessageThread.objects.first().messages.count(), prev_count + 1)

    def test_thread_latest_message(self):
        msg = Message.objects.create(
            recipient=self.receiver,
            sender=self.sender,
            subject='subject',
            body='newest',
        )
        self.thread.add_message(msg)
        self.assertEqual(
            MessageThread.objects.get(pk=self.thread.pk).latest.body, 
            'newest')

    
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


class InboxTests(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.usr = User.objects.create_user(username="someone")
        cls.receiver = User.objects.create_user(username="sometwo")

        cls.thread = MessageThread.objects.create(
            initiator=cls.usr
        )
        cls.inbox = Inbox.objects.create(user=cls.usr)
        cls.inbox.threads.add(cls.thread)
        cls.inbox.save()

    def setUp(self):
        pass

    def test_create_inbox(self):
        usr = User.objects.create_user(username="somefour")
        obj = Inbox.objects.create(user=usr)
        self.assertIsInstance(obj, Inbox)
        self.assertIsInstance(str(obj), str)

    def test_notifications_read(self):

        obj = Notification.objects.create(
            user=self.usr,
            title='Title',
            message="Message"
        )

        self.assertEqual(self.inbox.notifications.count(), 1)
        self.assertEqual(self.inbox.unread_notifications, 1)
        obj.read = True
        obj.save()
        self.assertEqual(self.inbox.unread_notifications, 0)
        obj.delete()

    def test_archived_threads(self):
        self.assertEqual(self.inbox.archived_threads.count(), 0)
        self.thread.closed=True
        self.thread.save()
        self.assertEqual(self.inbox.archived_threads.count(), 1)
        
        self.thread.closed=False
        self.thread.save()
        
    def test_unread_messages(self):
        self.assertEqual(self.inbox.unread_messages, 0)
        message = Message.objects.create(
            recipient=self.receiver,
            sender=self.usr,
            subject='subject',
            body='body',
        )
        self.thread.add_message(message)
        # TODO
        #self.assertEqual(Inbox.objects.first().unread_messages, 1)

    def test_total_in(self):
        self.assertEqual(self.inbox.total_in, 0)

    
    def test_receive_message(self):
        message = Message.objects.create(
            recipient=self.receiver,
            sender=self.usr,
            subject='subject',
            body='body',
        )
        prev_count = Inbox.objects.first().threads.count()
        self.inbox.receive_message(message)
        self.assertEqual(Inbox.objects.first().threads.count(), 
            prev_count + 1)

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