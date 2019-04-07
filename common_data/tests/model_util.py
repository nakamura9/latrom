from common_data import models
from django.contrib.auth.models import User
class CommonModelCreator():
    def __init__(self, klass):
        self.cls = klass

    def create_individual(self):
        self.cls.individual = models.Individual.objects.create(
            first_name="test",
            last_name="last_name"
            )

        return self.cls.individual

    def create_organization(self):
        self.cls.organization = models.Organization.objects.create(
            legal_name="business"
            )

        return self.cls.organization

    def create_user(self):
        if hasattr(self.cls, 'user'):
            return self.cls.user

        self.cls.user = User.objects.create_user('user', 
            email='test@user.com', 
            password='123')

        return self.cls.user