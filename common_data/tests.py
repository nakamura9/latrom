from django.test import TestCase
from django.contrib.auth.models import User

def create_test_user(cls):
    cls.user = User.objects.create(username='Testuser')
    cls.user.set_password('123')
    cls.user.save()
    print cls.user