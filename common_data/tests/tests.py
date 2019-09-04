from django.test import Client, TestCase
from common_data.models import *
import datetime
from .test_models import create_test_user, create_test_common_entities
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
import json
from common_data.utilities import (
    ConfigMixin, 
    ContextMixin, 
    extract_period, 
    time_choices)
import responses
import requests
import services
from common_data.tasks import license_verification_func
from services.tests.model_util import ServiceModelCreator

class ModelTests(TestCase):
    @classmethod 
    def setUpTestData(cls):
        cls.individual = Individual.objects.create(
            first_name='Test',
            last_name='Name'
        )
        cls.user = User.objects.create_superuser('Testuser', 
            'admin@test.com', '123')
        cls.user.save()

        cls.organization = Organization.objects.create(
            legal_name='Organization'
        )


    def test_person_full_name(self):
        #using individual as a template
        self.assertEqual(self.individual.full_name, 'Test Name')

    def test_create_individual(self):
        obj = Individual.objects.create(
            first_name='Test',
            last_name='Name'
        )
        self.assertIsInstance(obj, Individual)
        self.assertEqual(str(obj), 'Test Name')


    def test_delete_individual(self):
        obj = Individual.objects.create(
            first_name='Test',
            last_name='Name'
        )
        self.assertTrue(obj.active)
        obj.delete()
        self.assertFalse(obj.active)

    def test_create_note(self):
        obj = Note.objects.create(
            note='Note',
            author=self.user
        )
        self.assertIsInstance(obj, Note)

    def test_create_organization(self):
        obj = Organization.objects.create(
            legal_name='Organization'
        )
        self.assertIsInstance(obj, Organization)
        self.assertEqual(str(obj), 'Organization')

    def test_organization_members(self):
        org = Organization.objects.create(
            legal_name='Organization'
        )

        ind = Individual.objects.create(
            first_name='Test',
            last_name='Name'
        )

        self.assertEqual(org.members.count(), 0)
        org.add_member(ind)
        
        self.assertEqual(org.members.count(), 1)

    '''def test_config(self):
        #also validates singleton model
        obj = GlobalConfig.objects.create()
        self.assertIsInstance(obj, GlobalConfig)'''


class ViewTests(TestCase):
    fixtures = ['common.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    
    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)    
        create_test_common_entities(cls)

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_pagination_mixin(self):
        #tested in pages that inherit from it
        self.assertTrue(True)

    def test_get_organization_create_view(self):
        resp = self.client.get('/base/organization/create')
        self.assertEqual(resp.status_code, 200)

    def test_post_organization_create_view(self):
        resp = self.client.post('/base/organization/create',
            data={
              'legal_name': 'Name'  
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_organization_update_view(self):
        resp = self.client.get('/base/organization/update/' + '1')
        self.assertEqual(resp.status_code, 200)

    def test_post_organization_update_view(self):
        resp = self.client.post('/base/organization/update/' + '1',
            data={
              'legal_name': 'Name'  
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_organization_list(self):
        resp = self.client.get('/base/organization/list')
        self.assertEqual(resp.status_code, 200)

    def test_get_organization_detail(self):
        resp = self.client.get('/base/organization/detail/' + '1')
        self.assertEqual(resp.status_code, 200)

    def test_get_individual_create_view(self):
        resp = self.client.get('/base/individual/create')
        self.assertEqual(resp.status_code, 200)

    def test_post_individual_create_view(self):
        resp = self.client.post('/base/individual/create',
            data={
              'first_name': 'Name',
              'last_name': 'Name'  
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_individual_update_view(self):
        resp = self.client.get('/base/individual/update/' + '1')
        self.assertEqual(resp.status_code, 200)

    def test_post_individual_update_view(self):
        resp = self.client.post('/base/individual/update/' + '1',
            data={
              'first_name': 'Name',
              'last_name': 'Name'  
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_individual_list(self):
        resp = self.client.get('/base/individual/list')
        self.assertEqual(resp.status_code, 200)

    def test_get_individual_detail(self):
        resp = self.client.get('/base/individual/detail/' + '1')
        self.assertEqual(resp.status_code, 200)

    def test_get_send_mail_page(self):
        resp = self.client.get('/base/email')
        self.assertEqual(resp.status_code, 200)

    def test_post_send_mail_page(self):
        #TODO simulate email do research 
        self.assertTrue(True)

    def test_get_about_page(self):
        resp = self.client.get('/base/about')
        self.assertEqual(resp.status_code, 200)

    def test_get_workflow_page(self):
        #ensure that all links are shown
        resp = self.client.get('/base/workflow')
        self.assertEqual(resp.status_code, 302)
        settings = GlobalConfig.objects.first()
        settings.is_configured=True
        settings.save()

        resp = self.client.get('/base/workflow')
        self.assertEqual(resp.status_code, 200)
        settings.is_configured=False
        settings.save()


    def test_get_global_config_page(self):
        #ensure that all links are shown
        resp = self.client.get('/base/config/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_global_config_page(self):
        #ensure that all links are shown
        resp = self.client.post('/base/config/1',
            data={
                'email_user': 'username',
                'backup_frequency': 'D',
                'organization_name': 'latrom',
                'organization_address': 'somewhere',
                'logo_aspect_ratio': 0
            })
        
        self.assertEqual(resp.status_code, 302)

    def test_get_global_config_page_with_organization(self):
        #ensure that all links are shown
        config = GlobalConfig.objects.first()
        config.organization = self.organization
        config.save()
        resp = self.client.get('/base/config/1')
        self.assertEqual(resp.status_code, 200)

        config.organization = None
        config.save()

    def test_post_global_config_page_with_organization(self):
        #ensure that all links are shown
        config = GlobalConfig.objects.first()

        config.organization = self.organization
        config.save()
        resp = self.client.post('/base/config/1',
            data={
                'email_user': 'username',
                'backup_frequency': 'D',
                'organization_name': 'latrom',
                'organization_address': 'somewhere',
                'logo_aspect_ratio': 0
            })
        
        self.assertEqual(resp.status_code, 302)
        config.organization = None
        config.save()

    def test_reset_license_check(self):
        resp = self.client.get(reverse('base:reset-license-check'))
        #redirects
        self.assertEqual(resp.status_code, 302)

    def test_get_model_latest(self):
        resp = self.client.get(reverse('base:get-latest-model', kwargs={
            'model_name': 'organization',
            'app': 'common_data'
        }))
        self.assertEqual(resp.status_code, 200)
        org = Organization.objects.latest('pk')
        data = json.loads(resp.content)
        self.assertTrue(len(data['data']) == 2)

    def test_get_api_current_user(self):
        resp = self.client.get('/base/api/current-user')
        self.assertEqual(json.loads(resp.content)['name'], 'Testuser')


    def test_get_api_logo_url(self):
        resp = self.client.get('/base/logo-url')
        self.assertEqual(json.loads(resp.content)['url'], '')

    def test_get_authentication_view(self):
        resp = self.client.get('/base/authenticate')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_note(self):
        ServiceModelCreator(
            self).create_service_work_order()

        resp = self.client.post(reverse('base:create-note'), data={
            'author': User.objects.first().pk,
            'note': 'testing',
            'target': 'work_order',
            'target_id': 1
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['status'], 'ok')

    def test_current_db(self):
        resp = self.client.get('/base/api/current-db/')
        self.assertEqual(resp.status_code, 200)

class UtilityTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 'invoicing.json']

    def test_config_mixin(self):
        class ConfigChild(ConfigMixin):
            def get_context_data(self):
                return {}

        mixin = ConfigChild()
        self.assertIsInstance(mixin.get_context_data(), dict)

    def test_extra_context(self):
        class MixinParent(ContextMixin):
            def get_context_data(self):
                return {}

        mixin = MixinParent()
        self.assertIsInstance(mixin.get_context_data(), dict)


    def test_extract_period(self):
        start, end = extract_period({
            'start_period': '01/01/2018',
            'end_period': '12/31/2018'
        })
        self.assertEqual(start, datetime.datetime(2018, 1, 1, 0, 0))
        self.assertEqual(end, datetime.datetime(2018, 12, 31,0 ,0))
        start, end = extract_period({
            'default_periods': '1'
        })
        delta = datetime.date.today() - datetime.timedelta(days=7)
        self.assertEqual(start, delta)
        self.assertEqual(end, datetime.date.today())
        


    def test_time_choices(self):
        output = time_choices('06:00:00', '12:00:00', '00:30:00')
        self.assertEqual(len(output), 12)
        time = datetime.datetime.strptime('11:30:00', "%H:%M:%S").time()
        self.assertEqual(output[11][0], time)


class CommonDataWizardTests(TestCase):
    fixtures = ['common.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()
        create_test_user(cls)

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_global_config_wizard(self):
        config_data = {
            'config_wizard-current_step': 0,
            '0-organization_name': 'name',
            '0-organization_address': 'address',
            '0-backup_frequency': "D",
            '0-logo_aspect_ratio': 0

        }

        resp = self.client.post(reverse('base:config-wizard'), data=config_data)
        self.assertEqual(resp.status_code, 302)

class LicenseTaskTests(TestCase):
    fixtures = ['common.json']
    
    @classmethod
    def setUpTestData(cls):
        pass


    def test_verification(self):
        @responses.activate
        def responses_action():
            responses.add(responses.GET, 
                'http://nakamura9.pythonanywhere.com/validate',
                body=json.dumps({'status': 'valid'}))
            
            license = json.load(open('../license.json', 'r'))
            license_verification_func(license, 
                'http://nakamura9.pythonanywhere.com/validate')

        responses_action()
        settings = GlobalConfig.objects.first()
        self.assertEqual(settings.last_license_check, datetime.date.today())
