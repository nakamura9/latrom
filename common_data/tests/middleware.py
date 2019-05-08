from django.test import TestCase, Client
from django.http.request import HttpRequest
from common_data.middleware.license import LicenseMiddleware
from django.contrib.auth.models import User
import shutil
import latrom
from common_data.models import GlobalConfig
import os

class LicenseMiddlewareTest(TestCase):
    fixtures = ['common.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('Testuser', 'admin@mail.com', '123')
        
    

    def setUp(self):
        self.client.login(username='Testuser', password='123')
        self.config = GlobalConfig.objects.first()

    def test_license_check_with_no_license(self):
        shutil.move('license.json', 'assets')
        resp = self.client.get('/base/workflow')
        self.assertRedirects(resp, '/base/license-error-page')
        shutil.move(os.path.join('assets','license.json'), '.')

    def test_no_debug_license_middleware(self):
        latrom.settings.DEBUG=False
        self.config.verification_task_id = ""
        self.config.save()
        resp = self.client.get('/base/workflow')
        self.config = GlobalConfig.objects.first()
        self.assertTrue(self.config.verification_task_id != "")
        self.config.verification_task_id = ""
        self.config.save()
        latrom.settings.DEBUG = True

    def test_no_debug_license_middleware_with_task_id(self):
        latrom.settings.DEBUG=False
        self.config.verification_task_id = "28374hur98fwhf9832"
        resp = self.client.get('/base/workflow')
        #self.assertEqual(resp.status_code, 200)
        latrom.settings.DEBUG = True





